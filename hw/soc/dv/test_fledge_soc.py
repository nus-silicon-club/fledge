import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


GPIO_BASE = 0x4000_0000
TIMER_BASE = 0x4000_1000
UART_BASE = 0x4000_2000

GPIO_DATA_IN = 0x0
GPIO_DATA_OUT = 0x4
GPIO_OUT_EN = 0x8

TIMER_COUNT = 0x0
TIMER_COMPARE = 0x4
TIMER_CTRL = 0x8
TIMER_STATUS = 0xC

UART_TXDATA = 0x0
UART_STATUS = 0x4
UART_BAUDDIV = 0x8


async def reset(dut):
    dut.rst_ni.value = 0
    dut.reg_req_i.value = 0
    dut.reg_we_i.value = 0
    dut.reg_addr_i.value = 0
    dut.reg_wdata_i.value = 0
    dut.gpio_i.value = 0
    dut.uart_rx_i.value = 1

    for _ in range(3):
        await RisingEdge(dut.clk_i)

    dut.rst_ni.value = 1
    await RisingEdge(dut.clk_i)


async def bus_write(dut, addr, data):
    dut.reg_addr_i.value = addr
    dut.reg_wdata_i.value = data
    dut.reg_we_i.value = 1
    dut.reg_req_i.value = 1

    await RisingEdge(dut.clk_i)

    dut.reg_req_i.value = 0
    dut.reg_we_i.value = 0
    await RisingEdge(dut.clk_i)


async def bus_read(dut, addr):
    dut.reg_addr_i.value = addr
    dut.reg_we_i.value = 0
    dut.reg_req_i.value = 1

    await Timer(1, units="ns")

    value = int(dut.reg_rdata_o.value)
    assert int(dut.reg_ready_o.value) == 1

    await RisingEdge(dut.clk_i)

    dut.reg_req_i.value = 0
    await RisingEdge(dut.clk_i)

    return value


@cocotb.test()
async def test_reset_defaults_through_soc(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    assert int(dut.gpio_o.value) == 0
    assert int(dut.gpio_oe_o.value) == 0
    assert int(dut.uart_tx_o.value) == 1

    assert await bus_read(dut, GPIO_BASE + GPIO_DATA_OUT) == 0
    assert await bus_read(dut, GPIO_BASE + GPIO_OUT_EN) == 0
    assert await bus_read(dut, TIMER_BASE + TIMER_COUNT) == 0
    assert await bus_read(dut, TIMER_BASE + TIMER_COMPARE) == 0
    assert await bus_read(dut, TIMER_BASE + TIMER_CTRL) == 0
    assert await bus_read(dut, UART_BASE + UART_BAUDDIV) == 4


@cocotb.test()
async def test_gpio_address_decode(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, GPIO_BASE + GPIO_DATA_OUT, 0xA5A5_000F)
    await bus_write(dut, GPIO_BASE + GPIO_OUT_EN, 0x0000_00FF)

    assert int(dut.gpio_o.value) == 0xA5A5_000F
    assert int(dut.gpio_oe_o.value) == 0x0000_00FF
    assert await bus_read(dut, GPIO_BASE + GPIO_DATA_OUT) == 0xA5A5_000F
    assert await bus_read(dut, GPIO_BASE + GPIO_OUT_EN) == 0x0000_00FF

    dut.gpio_i.value = 0x1234_ABCD
    await Timer(1, units="ns")

    assert await bus_read(dut, GPIO_BASE + GPIO_DATA_IN) == 0x1234_ABCD


@cocotb.test()
async def test_timer_address_decode(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, TIMER_BASE + TIMER_COMPARE, 3)
    await bus_write(dut, TIMER_BASE + TIMER_CTRL, 1)

    for _ in range(4):
        await RisingEdge(dut.clk_i)

    count = await bus_read(dut, TIMER_BASE + TIMER_COUNT)
    status = await bus_read(dut, TIMER_BASE + TIMER_STATUS)

    assert count >= 3
    assert status & 0x1 == 1
    assert int(dut.timer_done_o.value) == 1


@cocotb.test()
async def test_uart_address_decode(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, UART_BASE + UART_BAUDDIV, 2)
    assert await bus_read(dut, UART_BASE + UART_BAUDDIV) == 2

    await bus_write(dut, UART_BASE + UART_TXDATA, 0x5A)
    status = await bus_read(dut, UART_BASE + UART_STATUS)

    assert status & 0x1 == 1


@cocotb.test()
async def test_unmapped_accesses_complete_without_side_effects(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, GPIO_BASE + GPIO_DATA_OUT, 0xCAFE_BABE)

    assert await bus_read(dut, 0x5000_0000) == 0
    assert await bus_read(dut, GPIO_BASE + 0x10) == 0

    await bus_write(dut, 0x5000_0000, 0xFFFF_FFFF)
    await bus_write(dut, GPIO_BASE + 0x10, 0x1234_5678)

    assert await bus_read(dut, GPIO_BASE + GPIO_DATA_OUT) == 0xCAFE_BABE
