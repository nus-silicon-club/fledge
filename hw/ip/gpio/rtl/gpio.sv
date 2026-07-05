module gpio #(
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

    input  logic [WIDTH-1:0] gpio_i,
    output logic [WIDTH-1:0] gpio_o,
    output logic [WIDTH-1:0] gpio_oe_o
);

  localparam logic [3:0] ADDR_DATA_IN  = 4'h0;
  localparam logic [3:0] ADDR_DATA_OUT = 4'h4;
  localparam logic [3:0] ADDR_OUT_EN   = 4'h8;

  logic [WIDTH-1:0] data_out_q;
  logic [WIDTH-1:0] out_en_q;

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      data_out_q <= '0;
      out_en_q   <= '0;
    end else if (reg_req_i && reg_we_i) begin
      unique case (reg_addr_i)
        ADDR_DATA_OUT: data_out_q <= reg_wdata_i;
        ADDR_OUT_EN:   out_en_q   <= reg_wdata_i;
        default:       ;
      endcase
    end
  end

  always_comb begin
    unique case (reg_addr_i)
      ADDR_DATA_IN:  reg_rdata_o = gpio_i;
      ADDR_DATA_OUT: reg_rdata_o = data_out_q;
      ADDR_OUT_EN:   reg_rdata_o = out_en_q;
      default:       reg_rdata_o = '0;
    endcase
  end

  assign reg_ready_o = reg_req_i;
  assign gpio_o      = data_out_q;
  assign gpio_oe_o   = out_en_q;

endmodule
