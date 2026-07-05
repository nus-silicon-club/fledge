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

    output logic             tx_o
);

  localparam logic [3:0] ADDR_TXDATA  = 4'h0;
  localparam logic [3:0] ADDR_STATUS  = 4'h4;
  localparam logic [3:0] ADDR_BAUDDIV = 4'h8;

  typedef enum logic [2:0] {
    StateIdle,
    StateStart,
    StateData,
    StateStop,
    StateDone
  } state_e;

  state_e state_q;
  logic [WIDTH-1:0] bauddiv_q;
  logic [WIDTH-1:0] baud_count_q;
  logic [7:0]       tx_shift_q;
  logic [2:0]       bit_idx_q;
  logic             tx_busy_q;
  logic             tx_done_q;

  wire write_txdata_w  = reg_req_i && reg_we_i && reg_addr_i == ADDR_TXDATA;
  wire write_bauddiv_w = reg_req_i && reg_we_i && reg_addr_i == ADDR_BAUDDIV;
  wire baud_tick_w     = baud_count_q == bauddiv_q - 1'b1;
  wire [WIDTH-1:0] bauddiv_next_w = reg_wdata_i == '0 ? {{(WIDTH-1){1'b0}}, 1'b1} : reg_wdata_i;

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      state_q      <= StateIdle;
      bauddiv_q    <= 32'd4;
      baud_count_q <= '0;
      tx_shift_q   <= '0;
      bit_idx_q    <= '0;
      tx_busy_q    <= 1'b0;
      tx_done_q    <= 1'b0;
      tx_o         <= 1'b1;
    end else begin
      // tx_done_q <= 1'b0;

      if (write_bauddiv_w) begin
        bauddiv_q <= bauddiv_next_w;
      end

      case (state_q)
        StateIdle: begin
          tx_o         <= 1'b1;
          tx_busy_q    <= 1'b0; // put here so tx_done stays high until next byte starts
          baud_count_q <= '0;
          bit_idx_q    <= '0;

          if (write_txdata_w) begin
            tx_shift_q <= reg_wdata_i[7:0];
            tx_busy_q  <= 1'b1;
            tx_done_q  <= 1'b0;
	    tx_o       <= 1'b0;
            state_q    <= StateStart;
          end
        end

        StateStart: begin
          tx_o      <= 1'b0;
          tx_busy_q <= 1'b1;

          if (baud_tick_w) begin
            baud_count_q <= '0;
            tx_o         <= tx_shift_q[0];
            state_q      <= StateData;
          end else begin
            baud_count_q <= baud_count_q + 1'b1;
          end
        end

        StateData: begin
          tx_o      <= tx_shift_q[bit_idx_q];
          tx_busy_q <= 1'b1;

          if (baud_tick_w) begin
            baud_count_q <= '0;

            if (bit_idx_q == 3'd7) begin
              tx_o    <= 1'b1;
              state_q <= StateStop;
            end else begin
              bit_idx_q <= bit_idx_q + 1'b1;
              tx_o      <= tx_shift_q[bit_idx_q + 1'b1];
            end
          end else begin
            baud_count_q <= baud_count_q + 1'b1;
          end
        end

        StateStop: begin
          tx_o      <= 1'b1;
          tx_busy_q <= 1'b1;

          if (baud_tick_w) begin
            baud_count_q <= '0;
            state_q      <= StateDone;
          end else begin
            baud_count_q <= baud_count_q + 1'b1;
          end
        end

        StateDone: begin
          tx_o      <= 1'b1;
          tx_busy_q <= 1'b0;
          tx_done_q <= 1'b1;
          state_q   <= StateIdle;
        end

        default: begin
          state_q <= StateIdle;
        end
      endcase
    end
  end

  always_comb begin
    case (reg_addr_i)
      ADDR_STATUS:  reg_rdata_o = {{(WIDTH-2){1'b0}}, tx_done_q, tx_busy_q};
      ADDR_BAUDDIV: reg_rdata_o = bauddiv_q;
      default:      reg_rdata_o = '0;
    endcase
  end

  assign reg_ready_o = reg_req_i;

endmodule
