# Memory Map

The machine-readable source of truth for the Fledge address map is:

```text
hw/soc/memory_map.yml
```

Keep this document and `hw/soc/memory_map.yml` in sync until documentation is
generated from the YAML source.

## Address Regions

| Address Range | Block | Description |
| --- | --- | --- |
| `0x4000_0000` - `0x4000_0FFF` | `gpio` | GPIO registers |
| `0x4000_1000` - `0x4000_1FFF` | `timer` | Timer registers |
| `0x4000_2000` - `0x4000_2FFF` | `uart` | UART registers |

Each block receives a 4 KiB address region. The Phase 5 IP blocks only consume
the low 4-bit byte offset inside each region.

## Active Offsets

For Phase 5, only offsets `0x0` through `0xF` are routed to the selected IP
block. The SoC wrapper passes address bits `[3:0]` to the selected IP register
interface.

Offsets `0x10` through `0xFFF` inside each 4 KiB region are currently reserved.
Reads from reserved offsets return zero. Writes to reserved offsets are ignored.

## Unmapped Addresses

Addresses outside the listed regions are unmapped.

Unmapped reads return zero. Unmapped writes are ignored. Unmapped accesses still
complete on the internal register bus.
