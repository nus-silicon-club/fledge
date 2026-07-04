"""
Cocotb testbench for the example counter IP.
This is the club's reference testbench -- copy this pattern for every
new IP: setup clock, apply reset, drive stimulus, check with asserts.
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


async def reset(dut):
    dut.rst_ni.value = 0
    dut.en_i.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk_i)
    dut.rst_ni.value = 1
    await RisingEdge(dut.clk_i)


@cocotb.test()
async def test_reset_value(dut):
    """After reset, count_o must be 0."""
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)
    assert dut.count_o.value == 0, f"expected 0 after reset, got {dut.count_o.value}"


@cocotb.test()
async def test_counts_when_enabled(dut):
    """count_o must increment by 1 each cycle while en_i is high."""
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    dut.en_i.value = 1
    # Settle cycle: a value written right after an awaited RisingEdge
    # takes effect from the *following* edge, not the current one.
    # Always budget one settle cycle after changing an input before
    # asserting on synchronous outputs -- this trips up almost everyone
    # the first time they write a cocotb testbench.
    await RisingEdge(dut.clk_i)

    for expected in range(1, 11):
        await RisingEdge(dut.clk_i)
        got = int(dut.count_o.value)
        assert got == expected, f"cycle {expected}: expected {expected}, got {got}"


@cocotb.test()
async def test_holds_when_disabled(dut):
    """count_o must not change while en_i is low."""
    cocotb.start_soon(Clock(dut.clk_i, 10, units="ns").start())
    await reset(dut)

    dut.en_i.value = 1
    await RisingEdge(dut.clk_i)  # settle cycle for the enable
    await RisingEdge(dut.clk_i)  # now actually counting

    dut.en_i.value = 0
    await RisingEdge(dut.clk_i)  # settle cycle for the disable
    # Only now has en_i=0 actually taken effect -- re-sample here,
    # not before the settle edge, or you'll capture a stale value.
    held_value = int(dut.count_o.value)

    for _ in range(5):
        await RisingEdge(dut.clk_i)
        got = int(dut.count_o.value)
        assert got == held_value, f"count changed while disabled: {held_value} -> {got}"
