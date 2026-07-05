# gpio

**Status:** draft
**Owner:** haushuan

## Purpose

`gpio` is the first nontrivial Fledge IP block. It teaches a simple
memory-mapped register interface, GPIO input sampling, GPIO output control,
and output-enable masking.

## Register Map

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x0` | `DATA_IN` | RO | Current GPIO input value |
| `0x4` | `DATA_OUT` | RW | GPIO output value |
| `0x8` | `OUT_EN` | RW | Output enable mask, 1 means output enabled |

## Ports

| Port | Dir | Width | Description |
| --- | --- | --- | --- |
| `clk_i` | in | 1 | Clock |
| `rst_ni` | in | 1 | Active-low synchronous reset |
| `reg_req_i` | in | 1 | Register access request |
| `reg_we_i` | in | 1 | Register write enable |
| `reg_addr_i` | in | 4 | Register byte address |
| `reg_wdata_i` | in | WIDTH | Register write data |
| `reg_rdata_o` | out | WIDTH | Register read data |
| `reg_ready_o` | out | 1 | Register access accepted |
| `gpio_i` | in | WIDTH | GPIO input pins |
| `gpio_o` | out | WIDTH | GPIO output value |
| `gpio_oe_o` | out | WIDTH | GPIO output enable |

## Verification Plan

- Reset clears `DATA_OUT` and `OUT_EN`.
- Writes to `DATA_OUT` update `gpio_o`.
- Writes to `OUT_EN` update `gpio_oe_o`.
- Reads from `DATA_IN` return `gpio_i`.
- Reads from writable registers return their stored value.
- Writes to `DATA_IN` are ignored.
