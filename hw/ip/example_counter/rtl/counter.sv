// Simple 8-bit up-counter with synchronous reset and enable.
// This is the club's "hello world" IP -- its only job is to prove
// the RTL -> simulation -> verification pipeline works end to end.
module counter #(
    parameter int WIDTH = 8
) (
    input  logic             clk_i,
    input  logic             rst_ni,   // active-low sync reset
    input  logic             en_i,
    output logic [WIDTH-1:0] count_o
);

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      count_o <= '0;
    end else if (en_i) begin
      count_o <= count_o + 1'b1;
    end
  end

endmodule
