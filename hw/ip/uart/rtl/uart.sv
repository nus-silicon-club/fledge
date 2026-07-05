module uart #(
    parameter int WIDTH = 32
) (
    input  logic             clk_i,
    input  logic             rst_ni,

    input  logic             reg_req_i,
    input  logic             reg_we_i,
    input  logic [3:0]       reg_addr_i,
    input  logic [WIDTH-1:0] reg_wdata_i,
    output logic [WIDTH-1:0] reg_rdata_o,
    output logic             reg_ready_o,

    input  logic             rx_i,
    output logic             tx_o
);

  localparam logic [3:0] ADDR_TXDATA  = 4'h0;
  localparam logic [3:0] ADDR_STATUS  = 4'h4;
  localparam logic [3:0] ADDR_BAUDDIV = 4'h8;
  localparam logic [3:0] ADDR_RXDATA  = 4'hC;

  typedef enum logic [2:0] {
    TxIdle,
    TxStart,
    TxData,
    TxStop,
    TxDone
  } tx_state_e;

  typedef enum logic [2:0] {
    RxIdle,
    RxStart,
    RxData,
    RxStop,
    RxDone
  } rx_state_e;

  tx_state_e tx_state_q;
  logic [WIDTH-1:0] tx_baud_count_q;
  logic [7:0]       tx_shift_q;
  logic [2:0]       tx_bit_idx_q;
  logic             tx_busy_q;
  logic             tx_done_q;

  rx_state_e rx_state_q;
  logic [WIDTH-1:0] rx_baud_count_q;
  logic [7:0]       rx_shift_q;
  logic [2:0]       rx_bit_idx_q;
  logic [7:0]       rx_data_q;
  logic             rx_valid_q;

  logic [WIDTH-1:0] bauddiv_q;

  wire write_txdata_w  = reg_req_i && reg_we_i && reg_addr_i == ADDR_TXDATA;
  wire write_bauddiv_w = reg_req_i && reg_we_i && reg_addr_i == ADDR_BAUDDIV;
  wire read_rxdata_w   = reg_req_i && !reg_we_i && reg_addr_i == ADDR_RXDATA;

  wire [WIDTH-1:0] bauddiv_next_w = reg_wdata_i == '0 ? {{(WIDTH-1){1'b0}}, 1'b1} : reg_wdata_i;
  wire tx_baud_tick_w = tx_baud_count_q == bauddiv_q - 1'b1;
  wire rx_baud_tick_w = rx_baud_count_q == bauddiv_q - 1'b1;
  wire rx_half_tick_w = rx_baud_count_q == (bauddiv_q >> 1);

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      bauddiv_q       <= 32'd4;

      tx_state_q      <= TxIdle;
      tx_baud_count_q <= '0;
      tx_shift_q      <= '0;
      tx_bit_idx_q    <= '0;
      tx_busy_q       <= 1'b0;
      tx_done_q       <= 1'b0;
      tx_o            <= 1'b1;

      rx_state_q      <= RxIdle;
      rx_baud_count_q <= '0;
      rx_shift_q      <= '0;
      rx_bit_idx_q    <= '0;
      rx_data_q       <= '0;
      rx_valid_q      <= 1'b0;
    end else begin
      if (write_bauddiv_w) begin
        bauddiv_q <= bauddiv_next_w;
      end

      if (read_rxdata_w) begin
        rx_valid_q <= 1'b0;
      end

      case (tx_state_q)
        TxIdle: begin
          tx_o            <= 1'b1;
          tx_busy_q       <= 1'b0;
          tx_baud_count_q <= '0;
          tx_bit_idx_q    <= '0;

          if (write_txdata_w) begin
            tx_shift_q <= reg_wdata_i[7:0];
            tx_busy_q  <= 1'b1;
            tx_done_q  <= 1'b0;
            tx_o       <= 1'b0;
            tx_state_q <= TxStart;
          end
        end

        TxStart: begin
          tx_o      <= 1'b0;
          tx_busy_q <= 1'b1;

          if (tx_baud_tick_w) begin
            tx_baud_count_q <= '0;
            tx_o            <= tx_shift_q[0];
            tx_state_q      <= TxData;
          end else begin
            tx_baud_count_q <= tx_baud_count_q + 1'b1;
          end
        end

        TxData: begin
          tx_o      <= tx_shift_q[tx_bit_idx_q];
          tx_busy_q <= 1'b1;

          if (tx_baud_tick_w) begin
            tx_baud_count_q <= '0;

            if (tx_bit_idx_q == 3'd7) begin
              tx_o       <= 1'b1;
              tx_state_q <= TxStop;
            end else begin
              tx_bit_idx_q <= tx_bit_idx_q + 1'b1;
              tx_o         <= tx_shift_q[tx_bit_idx_q + 1'b1];
            end
          end else begin
            tx_baud_count_q <= tx_baud_count_q + 1'b1;
          end
        end

        TxStop: begin
          tx_o      <= 1'b1;
          tx_busy_q <= 1'b1;

          if (tx_baud_tick_w) begin
            tx_baud_count_q <= '0;
            tx_state_q      <= TxDone;
          end else begin
            tx_baud_count_q <= tx_baud_count_q + 1'b1;
          end
        end

        TxDone: begin
          tx_o       <= 1'b1;
          tx_busy_q  <= 1'b0;
          tx_done_q  <= 1'b1;
          tx_state_q <= TxIdle;
        end

        default: begin
          tx_state_q <= TxIdle;
        end
      endcase

      case (rx_state_q)
        RxIdle: begin
          rx_baud_count_q <= '0;
          rx_bit_idx_q    <= '0;

          if (!rx_i) begin
            rx_state_q <= RxStart;
          end
        end

        RxStart: begin
          if (rx_half_tick_w) begin
            if (!rx_i) begin
              rx_baud_count_q <= '0;
              rx_state_q      <= RxData;
            end else begin
              rx_baud_count_q <= '0;
              rx_state_q      <= RxIdle;
            end
          end else begin
            rx_baud_count_q <= rx_baud_count_q + 1'b1;
          end
        end

        RxData: begin
          if (rx_baud_tick_w) begin
            rx_shift_q[rx_bit_idx_q] <= rx_i;
            rx_baud_count_q          <= '0;

            if (rx_bit_idx_q == 3'd7) begin
              rx_state_q <= RxStop;
            end else begin
              rx_bit_idx_q <= rx_bit_idx_q + 1'b1;
            end
          end else begin
            rx_baud_count_q <= rx_baud_count_q + 1'b1;
          end
        end

        RxStop: begin
          if (rx_baud_tick_w) begin
            rx_baud_count_q <= '0;

            if (rx_i) begin
              rx_state_q <= RxDone;
            end else begin
              rx_state_q <= RxIdle;
            end
          end else begin
            rx_baud_count_q <= rx_baud_count_q + 1'b1;
          end
        end

        RxDone: begin
          rx_data_q  <= rx_shift_q;
          rx_valid_q <= 1'b1;
          rx_state_q <= RxIdle;
        end

        default: begin
          rx_state_q <= RxIdle;
        end
      endcase
    end
  end

  always_comb begin
    case (reg_addr_i)
      ADDR_STATUS:  reg_rdata_o = {{(WIDTH-3){1'b0}}, rx_valid_q, tx_done_q, tx_busy_q};
      ADDR_BAUDDIV: reg_rdata_o = bauddiv_q;
      ADDR_RXDATA:  reg_rdata_o = {{(WIDTH-8){1'b0}}, rx_data_q};
      default:      reg_rdata_o = '0;
    endcase
  end

  assign reg_ready_o = reg_req_i;

endmodule
