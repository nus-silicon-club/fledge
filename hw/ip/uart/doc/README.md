# uart

**Status:** draft
**Owner:** haushuan

## Purpose

`uart` is a simple memory-mapped UART transmitter. This first version supports
one-byte TX and RX without FIFOs, interrupts, parity, or flow control.

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
| `0x4` | `STATUS` | RO | Bit 0: `tx_busy`, bit 1: sticky `tx_done`, bit 2: sticky `rx_valid`  |
| `0x8` | `BAUDDIV` | RW | Number of clock cycles per UART bit |
| `0xC` | `RXDATA`  | RO | Bits `[7:0]` last received byte; reading clears `rx_valid` | 

## Behaviour

- Writing `TXDATA` starts a transmit frame if TX is idle.
- Writes to `TXDATA` while TX is busy are ignored.
- `tx_done` sets after a transmit frame completes and clears when a new byte starts.
- RX samples incoming data near the middle of each bit period.
- `rx_valid` sets after a valid stop bit and clears when `RXDATA` is read.
- If a new byte is received before `RXDATA` is read, the latest byte replaces the previous one.

## Verification Plan

- Reset leaves `tx_o` idle high and clears status. 
- `BAUDDIV` can be written and read back.
- TX sends start bit, 8 data bits LSB-first, and stop bit.
- `tx_busy` is high during transmission.
- `tx_done` sets after transmission. 
- RX captures injected UART frames.
- RX sets `rx_valid` after a complete frame.
- Reading `RXDATA` clears `rx_valid`.
- TX-to-RX loopback transfers a byte end-to-end.
