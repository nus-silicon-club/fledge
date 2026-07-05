import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


COUNT = 0x0
COMPARE = 0x4
CTRL = 0x8
STATUS = 0xC


async def reset(dut):
    dut.rst_ni.value = 0
    dut.reg_req_i.value = 0
    dut.reg_we_i.value = 0
    dut.reg_addr_i.value = 0
    dut.reg_wdata_i.value = 0
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
    await RisingEdge(dut.clk_i)
    dut.reg_req_i.value = 0
    await RisingEdge(dut.clk_i)
    return value


@cocotb.test()
async def test_reset_defaults(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    assert await bus_read(dut, COUNT) == 0
    assert await bus_read(dut, COMPARE) == 0
    assert await bus_read(dut, CTRL) == 0


@cocotb.test()
async def test_compare_write_readback(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, COMPARE, 7)
    assert await bus_read(dut, COMPARE) == 7


@cocotb.test()
async def test_enable_counts(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, CTRL, 1)
    for _ in range(4):
        await RisingEdge(dut.clk_i)

    assert await bus_read(dut, COUNT) >= 3


@cocotb.test()
async def test_clear_resets_count(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, CTRL, 1)
    for _ in range(4):
        await RisingEdge(dut.clk_i)

    await bus_write(dut, CTRL, 0x2)
    assert await bus_read(dut, COUNT) == 0


@cocotb.test()
async def test_done_status(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, COMPARE, 3)
    await bus_write(dut, CTRL, 1)

    for _ in range(5):
        await RisingEdge(dut.clk_i)

    assert int(dut.done_o.value) == 1
    assert await bus_read(dut, STATUS) == 1
