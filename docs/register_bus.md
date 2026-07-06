# Register Bus

Fledge Phase 5 uses a small internal register bus to connect the CPU-less SoC
testbench master to memory-mapped peripheral registers.

This bus is intentionally simpler than OBI, APB, or AXI-Lite. Bus-specific
wrappers can be added later without changing reusable IP internals.

## Signals

| Signal | Direction From Master | Description |
| --- | --- | --- |
| `reg_req_i` | output | Register access request |
| `reg_we_i` | output | Write enable; `1` means write, `0` means read |
| `reg_addr_i` | output | Byte address |
| `reg_wdata_i` | output | Write data |
| `reg_rdata_o` | input | Read data |
| `reg_ready_o` | input | Access accepted/completed |

At the SoC wrapper boundary, `reg_addr_i` is a full byte address.

At each current IP boundary, `reg_addr_i` is the low register byte offset for
that IP. The Phase 5 SoC wrapper passes address bits `[3:0]` to the selected IP.

## Transfer Behavior

The Phase 5 register bus is a one-cycle, no-stall interface.

A transfer is active when `reg_req_i` is high. For writes, `reg_we_i` is high
and `reg_wdata_i` contains the write data. For reads, `reg_we_i` is low and
`reg_rdata_o` contains the read data.

Current IP blocks assert `reg_ready_o` when `reg_req_i` is asserted.

## Address Behavior

Valid accesses are decoded by the SoC wrapper using `docs/memory_map.md` and
`hw/soc/memory_map.yml`.

Unmapped reads return zero.

Unmapped writes are ignored.

Unmapped accesses still assert `reg_ready_o` when `reg_req_i` is asserted.
