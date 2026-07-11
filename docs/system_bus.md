# Fledge System Bus

## Purpose

The Fledge system bus connects CPU bus masters to memories and memory-mapped
peripherals.

It is an OBI-like request/grant and response protocol designed to match the
Ibex instruction and data interfaces without making reusable peripheral
internals depend directly on Ibex.

This interface replaces the one-cycle assumptions of the Phase 5 internal
register bus at the SoC integration boundary. GPIO, timer, and UART may remain
behind an adapter while their register interfaces are migrated incrementally.

## Design Goals

The first system bus supports:

- separate instruction and data masters,
- delayed request acceptance,
- delayed read and write responses,
- byte write enables,
- explicit access errors,
- memories and memory-mapped peripherals,
- one outstanding transaction per master,
- finite-latency verification models.

The first version does not support:

- multiple outstanding transactions from one master,
- transaction IDs,
- bursts,
- out-of-order responses,
- caches or coherency,
- atomic operations,
- clock-domain crossing.

## Signals

| Signal | Master direction | Width | Description |
| --- | --- | ---: | --- |
| `req` | output | 1 | Request is valid |
| `gnt` | input | 1 | Request has been accepted |
| `addr` | output | 32 | Byte address |
| `we` | output | 1 | Write enable |
| `be` | output | 4 | Byte enables |
| `wdata` | output | 32 | Write data |
| `rvalid` | input | 1 | Transaction response is valid |
| `rdata` | input | 32 | Read response data |
| `err` | input | 1 | Transaction completed with an error |

Instruction masters do not use `we`, `be`, or `wdata`.

## Request Phase

A master begins a transaction by asserting `req`.

While `req` is asserted and before `gnt` is observed, the master must keep
`addr`, `we`, `be`, and `wdata` stable.

A slave or interconnect accepts the request by asserting `gnt`. The request is
transferred on a rising clock edge when both `req` and `gnt` are high. After
that edge, the master may deassert `req`.

Grant does not complete the transaction. Completion occurs during the response
phase.

## Response Phase

Every accepted transaction receives exactly one response. The slave completes
a transaction by asserting `rvalid` for one clock cycle.

For a successful read:

```text
rvalid = 1
err    = 0
rdata  = requested data
```

For a successful write:

```text
rvalid = 1
err    = 0
rdata  = 0
```

For a failed access:

```text
rvalid = 1
err    = 1
rdata  = 0
```

The first implementation permits only one outstanding transaction per master.
A master must not receive a second grant before the response to its previous
transaction.

## Reads And Writes

A data read uses `we = 0` and `be = 0`. The value of `wdata` is ignored. An
instruction fetch is always a read.

A write uses `we = 1`. Each bit of `be` controls one byte of `wdata`:

| `be` bit | Data bits | Addressed byte |
| --- | --- | --- |
| `be[0]` | `wdata[7:0]` | `addr + 0` |
| `be[1]` | `wdata[15:8]` | `addr + 1` |
| `be[2]` | `wdata[23:16]` | `addr + 2` |
| `be[3]` | `wdata[31:24]` | `addr + 3` |

Memories must honor valid byte enables. Peripheral registers must either honor
a byte-enable pattern or return an error. They must not silently convert an
unsupported partial write into a full-word write.

## Address Alignment

The bus carries byte addresses. Instruction-fetch alignment follows the
configured RISC-V ISA.

For data accesses, the address and byte-enable combination must describe a
valid access. Invalid or unsupported combinations return an error. The
addressed slave or its adapter checks alignment; the interconnect performs
address routing rather than register-specific access policy.

## Errors

The following accesses return an error unless a later specification states
otherwise:

- unmapped addresses,
- reserved peripheral offsets,
- writes to read-only registers,
- unsupported byte-enable combinations,
- instruction fetches from non-executable regions,
- writes to read-only boot memory.

An error is a completed transaction. The slave must assert `rvalid` with `err`
rather than leaving the master stalled indefinitely.

## Reset Behavior

After reset:

- masters deassert `req`,
- slaves and interconnects deassert `gnt`,
- slaves and interconnects deassert `rvalid`,
- no transaction is considered outstanding.

No response may be generated for a request that was not accepted.

## Interconnect Rules

For each request:

- at most one slave may receive the request,
- at most one slave may grant the request,
- exactly one response must return after a grant,
- the response must return to the master that issued the request,
- unmapped requests must be handled by a default error responder.

The initial instruction and data paths remain separate. The instruction path
routes only to executable memory. The data path routes to boot memory, writable
data memory, GPIO, timer, UART, or the default error responder.

## Register-Bus Adapter

During migration, an adapter may connect the system bus to the Phase 5
one-cycle register bus. The adapter must:

1. accept at most one system-bus request,
2. capture its address, control, and write data,
3. issue one register-bus request,
4. capture register read data and status,
5. return one system-bus response,
6. reject unsupported accesses explicitly,
7. prevent duplicate register writes while the upstream request remains high.

A direct combinational connection from `req` to `reg_req_i` is not sufficient
because the system bus separates grant from response.

## Verification Requirements

Self-checking tests must cover:

- immediate grant and response,
- delayed grant,
- delayed response,
- read data returned with `rvalid`,
- full-word and supported byte writes,
- explicit error responses,
- one response per accepted request,
- no response without an accepted request,
- stable request fields before grant,
- no duplicate writes,
- unmapped address handling,
- reset with a pending or outstanding request.

Tests must use finite timeouts.
