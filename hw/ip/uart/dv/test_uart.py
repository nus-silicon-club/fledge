import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


TXDATA = 0x0
STATUS = 0x4
BAUDDIV = 0x8

TX_BUSY = 0x1
TX_DONE = 0x2


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
    assert int(dut.reg_ready_o.value) == 1
    await RisingEdge(dut.clk_i)
    dut.reg_req_i.value = 0
    await RisingEdge(dut.clk_i)
    return value


async def wait_cycles(dut, cycles):
    for _ in range(cycles):
        await RisingEdge(dut.clk_i)


async def sample_uart_frame(dut, bauddiv):
    bits = []

    while int(dut.tx_o.value) != 0:
        await RisingEdge(dut.clk_i)

    for _ in range(bauddiv // 2):
        await RisingEdge(dut.clk_i)

    for _ in range(10):
        bits.append(int(dut.tx_o.value))
        await wait_cycles(dut, bauddiv)

    return bits


def expected_frame(byte):
    bits = [0]
    bits.extend((byte >> bit) & 1 for bit in range(8))
    bits.append(1)
    return bits


@cocotb.test()
async def test_reset_idle_high(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    assert int(dut.tx_o.value) == 1
    assert await bus_read(dut, STATUS) == 0


@cocotb.test()
async def test_bauddiv_write_readback(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    await bus_write(dut, BAUDDIV, 6)
    assert await bus_read(dut, BAUDDIV) == 6


@cocotb.test()
async def test_transmits_uart_frame(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    bauddiv = 4
    byte = 0xA5

    await bus_write(dut, BAUDDIV, bauddiv)
    await bus_write(dut, TXDATA, byte)

    bits = await sample_uart_frame(dut, bauddiv)
    assert bits == expected_frame(byte), f"expected {expected_frame(byte)}, got {bits}"


@cocotb.test()
async def test_busy_and_done_status(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    bauddiv = 4

    await bus_write(dut, BAUDDIV, bauddiv)
    await bus_write(dut, TXDATA, 0x3C)

    status = await bus_read(dut, STATUS)
    assert status & TX_BUSY

    await wait_cycles(dut, bauddiv * 12)

    status = await bus_read(dut, STATUS)
    assert status & TX_DONE

@cocotb.test()
async def test_write_while_busy_does_not_corrupt_frame(dut):
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    bauddiv = 4
    first_byte = 0x55
    second_byte = 0xAA

    await bus_write(dut, BAUDDIV, bauddiv)

    sampler = cocotb.start_soon(sample_uart_frame(dut, bauddiv))

    await bus_write(dut, TXDATA, first_byte)
    await wait_cycles(dut, bauddiv * 2)
    await bus_write(dut, TXDATA, second_byte)

    bits = await sampler
    assert bits == expected_frame(first_byte), f"busy write corrupted frame: {bits}"
