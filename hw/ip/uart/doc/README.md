# uart

**Status:** draft
**Owner:** haushuan

## Purpose

`uart` is a simple memory-mapped UART transmitter. This first version supports
TX only: software writes one byte to `TXDATA`, and the block serializes it as a
UART frame on `tx_o`.

## Frame Format

- Idle level: high
- Start bit: low
- Data bits: 8 bits, least-significant bit first
- Stop bit: high
- Parity: none

## Register Map

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0x0` | `TXDATA` | WO | Bits `[7:0]` byte to transmit |
| `0x4` | `STATUS` | RO | Bit 0: `tx_busy`, bit 1: sticky `tx_done` |
| `0x8` | `BAUDDIV` | RW | Number of clock cycles per UART bit |

## Verification Plan

- Reset leaves `tx_o` idle high.
- `BAUDDIV` can be written and read back.
- Writing `TXDATA` starts a UART frame.
- Transmitted frame has start bit, 8 data bits LSB-first, and stop bit.
- `tx_busy` is high during transmission.
- `tx_done` sets after the frame completes and clears when a new byte starts. 
- Writes to `TXDATA` while busy do not corrupt the active frame.
