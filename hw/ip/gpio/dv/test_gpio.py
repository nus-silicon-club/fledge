import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


DATA_IN = 0x0
DATA_OUT = 0x4
OUT_EN = 0x8


async def reset(dut):
    dut.rst_ni.value = 0
    dut.reg_req_i.value = 0
    dut.reg_we_i.value = 0
    dut.reg_addr_i.value = 0
    dut.reg_wdata_i.value = 0
    dut.gpio_i.value = 0
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
async def test_reset_defaults(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    assert int(dut.gpio_o.value) == 0
    assert int(dut.gpio_oe_o.value) == 0
    assert await bus_read(dut, DATA_OUT) == 0
    assert await bus_read(dut, OUT_EN) == 0


@cocotb.test()
async def test_data_out_write_and_readback(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, DATA_OUT, 0xA5A5_000F)

    assert int(dut.gpio_o.value) == 0xA5A5_000F
    assert await bus_read(dut, DATA_OUT) == 0xA5A5_000F


@cocotb.test()
async def test_out_enable_write_and_readback(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, OUT_EN, 0x0000_00FF)

    assert int(dut.gpio_oe_o.value) == 0x0000_00FF
    assert await bus_read(dut, OUT_EN) == 0x0000_00FF


@cocotb.test()
async def test_data_in_reads_gpio_input(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    dut.gpio_i.value = 0x1234_ABCD
    await Timer(1, units="ns")

    assert await bus_read(dut, DATA_IN) == 0x1234_ABCD


@cocotb.test()
async def test_data_in_is_read_only(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    dut.gpio_i.value = 0x55AA_55AA
    await bus_write(dut, DATA_IN, 0xFFFF_FFFF)

    assert await bus_read(dut, DATA_IN) == 0x55AA_55AA
    assert int(dut.gpio_o.value) == 0
    assert int(dut.gpio_oe_o.value) == 0
