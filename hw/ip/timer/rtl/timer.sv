module timer #(
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

    output logic             done_o
);

  localparam logic [3:0] ADDR_COUNT   = 4'h0;
  localparam logic [3:0] ADDR_COMPARE = 4'h4;
  localparam logic [3:0] ADDR_CTRL    = 4'h8;
  localparam logic [3:0] ADDR_STATUS  = 4'hC;

  logic [WIDTH-1:0] count_q;
  logic [WIDTH-1:0] compare_q;
  logic             enable_q;

  wire clear_w = reg_req_i && reg_we_i && reg_addr_i == ADDR_CTRL && reg_wdata_i[1];

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      count_q   <= '0;
      compare_q <= '0;
      enable_q  <= 1'b0;
    end else begin
      if (reg_req_i && reg_we_i) begin
        case (reg_addr_i)
          ADDR_COMPARE: compare_q <= reg_wdata_i;
          ADDR_CTRL:    enable_q  <= reg_wdata_i[0];
          default:      ;
        endcase
      end

      if (clear_w) begin
        count_q <= '0;
      end else if (enable_q) begin
        count_q <= count_q + 1'b1;
      end
    end
  end

  assign done_o = count_q >= compare_q;

  always_comb begin
    case (reg_addr_i)
      ADDR_COUNT:   reg_rdata_o = count_q;
      ADDR_COMPARE: reg_rdata_o = compare_q;
      ADDR_CTRL:    reg_rdata_o = {{(WIDTH-1){1'b0}}, enable_q};
      ADDR_STATUS:  reg_rdata_o = {{(WIDTH-1){1'b0}}, done_o};
      default:      reg_rdata_o = '0;
    endcase
  end

  assign reg_ready_o = reg_req_i;

endmodule
