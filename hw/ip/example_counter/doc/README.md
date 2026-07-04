# example_counter

**Status:** verified
**Owner:** (assign when you form the club)

## Spec
An N-bit up-counter (default 8-bit). Synchronous active-low reset. Counts up
by 1 every cycle while `en_i` is high; holds its value while `en_i` is low.

| Port      | Dir | Width | Description              |
|-----------|-----|-------|---------------------------|
| clk_i     | in  | 1     | Clock                     |
| rst_ni    | in  | 1     | Active-low sync reset     |
| en_i      | in  | 1     | Count enable              |
| count_o   | out | WIDTH | Current count             |

## Why this block exists
This is not a real project deliverable -- it's the club's "hello world."
Its only job is to prove the RTL -> cocotb -> Verilator pipeline works
end to end, and to give every new member a template testbench to copy.

## Verification notes (read this before writing your own testbench)
When you drive an input signal in cocotb (e.g. `dut.en_i.value = 1`)
immediately after an `await RisingEdge(...)`, that change does **not**
affect the very next edge -- it takes effect from the edge *after* that.
Always insert one "settle" `await RisingEdge(...)` after changing an
input, before you trust a synchronous output against it. This bit us
in the very first draft of `test_counter.py`; see the comments in that
file for the working pattern.

## Status history
- Verified against Verilator 5.020 + cocotb 1.9.2, 3/3 tests passing.
