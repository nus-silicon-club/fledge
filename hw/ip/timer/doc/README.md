# timer

**Status:** draft
**Owner:** haushuan

## Purpose

`timer` is a simple memory-mapped counter/compare timer. It teaches register
state, counter behaviour, status flags, and clear/enable control.

## Register Map

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x0` | `COUNT` | RO | Current counter value |
| `0x4` | `COMPARE` | RW | Compare value |
| `0x8` | `CTRL` | RW | Bit 0: enable, bit 1: clear |
| `0xC` | `STATUS` | RO | Bit 0: done |

## Verification Plan

- Reset clears count, compare, and control state.
- Writing `COMPARE` updates compare value.
- Setting enable increments count.
- Clearing resets count.
- `done_o` and `STATUS.done` assert when `COUNT >= COMPARE`.
