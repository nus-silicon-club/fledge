module fledge_soc #(
    parameter int DATA_WIDTH = 32
) (
    input  logic                  clk_i,
    input  logic                  rst_ni,

    input  logic                  reg_req_i,
    input  logic                  reg_we_i,
    input  logic [31:0]           reg_addr_i,
    input  logic [DATA_WIDTH-1:0] reg_wdata_i,
    output logic [DATA_WIDTH-1:0] reg_rdata_o,
    output logic                  reg_ready_o,

    input  logic [DATA_WIDTH-1:0] gpio_i,
    output logic [DATA_WIDTH-1:0] gpio_o,
    output logic [DATA_WIDTH-1:0] gpio_oe_o,

    output logic                  timer_done_o,

    input  logic                  uart_rx_i,
    output logic                  uart_tx_o
);

  localparam logic [31:0] GPIO_BASE_ADDR  = 32'h4000_0000;
  localparam logic [31:0] TIMER_BASE_ADDR = 32'h4000_1000;
  localparam logic [31:0] UART_BASE_ADDR  = 32'h4000_2000;

  logic                  gpio_req_w;
  logic                  timer_req_w;
  logic                  uart_req_w;

  logic [DATA_WIDTH-1:0] gpio_rdata_w;
  logic [DATA_WIDTH-1:0] timer_rdata_w;
  logic [DATA_WIDTH-1:0] uart_rdata_w;

  logic                  gpio_ready_w;
  logic                  timer_ready_w;
  logic                  uart_ready_w;

  logic                  gpio_region_w;
  logic                  timer_region_w;
  logic                  uart_region_w;
  logic                  active_offset_w;
  logic [3:0]            ip_addr_w;

  assign gpio_region_w  = reg_addr_i[31:12] == GPIO_BASE_ADDR[31:12];
  assign timer_region_w = reg_addr_i[31:12] == TIMER_BASE_ADDR[31:12];
  assign uart_region_w  = reg_addr_i[31:12] == UART_BASE_ADDR[31:12];

  assign active_offset_w = reg_addr_i[11:4] == 8'h00;
  assign ip_addr_w       = reg_addr_i[3:0];

  assign gpio_req_w  = reg_req_i && active_offset_w && gpio_region_w;
  assign timer_req_w = reg_req_i && active_offset_w && timer_region_w;
  assign uart_req_w  = reg_req_i && active_offset_w && uart_region_w;

  gpio #(
      .WIDTH(DATA_WIDTH)
  ) u_gpio (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .reg_req_i(gpio_req_w),
      .reg_we_i(reg_we_i),
      .reg_addr_i(ip_addr_w),
      .reg_wdata_i(reg_wdata_i),
      .reg_rdata_o(gpio_rdata_w),
      .reg_ready_o(gpio_ready_w),
      .gpio_i(gpio_i),
      .gpio_o(gpio_o),
      .gpio_oe_o(gpio_oe_o)
  );

  timer #(
      .WIDTH(DATA_WIDTH)
  ) u_timer (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .reg_req_i(timer_req_w),
      .reg_we_i(reg_we_i),
      .reg_addr_i(ip_addr_w),
      .reg_wdata_i(reg_wdata_i),
      .reg_rdata_o(timer_rdata_w),
      .reg_ready_o(timer_ready_w),
      .done_o(timer_done_o)
  );

  uart #(
      .WIDTH(DATA_WIDTH)
  ) u_uart (
      .clk_i(clk_i),
      .rst_ni(rst_ni),
      .reg_req_i(uart_req_w),
      .reg_we_i(reg_we_i),
      .reg_addr_i(ip_addr_w),
      .reg_wdata_i(reg_wdata_i),
      .reg_rdata_o(uart_rdata_w),
      .reg_ready_o(uart_ready_w),
      .rx_i(uart_rx_i),
      .tx_o(uart_tx_o)
  );

  always_comb begin
    reg_rdata_o = '0;
    reg_ready_o = reg_req_i;

    unique case (1'b1)
      gpio_req_w: begin
        reg_rdata_o = gpio_rdata_w;
        reg_ready_o = gpio_ready_w;
      end

      timer_req_w: begin
        reg_rdata_o = timer_rdata_w;
        reg_ready_o = timer_ready_w;
      end

      uart_req_w: begin
        reg_rdata_o = uart_rdata_w;
        reg_ready_o = uart_ready_w;
      end

      default: begin
        reg_rdata_o = '0;
        reg_ready_o = reg_req_i;
      end
    endcase
  end

endmodule
