# Ibex CPU Integration Plan

## Purpose

Phase 6 prepares Fledge to integrate a production-quality RISC-V CPU without
importing or wiring CPU RTL yet.

This document selects the first CPU target and defines the dependency, bus,
memory, software, and verification work required for integration. The Phase 5
CPU-less SoC remains a required regression baseline.

## CPU Decision

Fledge will use lowRISC Ibex as its first CPU integration target.

Ibex is selected because it provides:

- production-quality SystemVerilog RTL,
- extensive upstream verification,
- separate instruction and data interfaces,
- explicit request, grant, response, and error signaling,
- byte-enabled data writes,
- standard RISC-V interrupt inputs,
- optional PMP, debug, cache, and security features,
- an architecture suitable for later FPGA and ASIC work.

The added integration complexity is intentional. Fledge will build the
infrastructure required to handle that complexity explicitly.

Ibex is external RTL. It must not be copied into `hw/ip/`.

Official references:

- <https://github.com/lowRISC/ibex>
- <https://ibex-core.readthedocs.io/en/latest/>
- <https://ibex-core.readthedocs.io/en/latest/02_user/integration.html>

## Initial Configuration

The first integration will use Ibex's supported `small` configuration rather
than inventing a custom parameter combination.

The expected configuration includes:

- RV32IMC,
- 32 integer registers,
- two-stage pipeline,
- three-cycle multiplier,
- compressed instructions,
- flip-flop register file,
- no instruction cache,
- no branch prediction,
- no PMP initially,
- no debug module initially,
- no SecureIbex features initially.

The exact configuration must come from the pinned Ibex revision's named
configuration data. Fledge documentation must not assume that upstream
parameter defaults remain unchanged.

Use `RegFileFF` for Verilator simulation. The latch-based register file is not
suitable for the current Verilator flow.

## Dependency Policy

Ibex must be pinned to a reviewed revision. The integration must record:

- repository URL,
- exact revision,
- license,
- selected RTL source set,
- selected named configuration,
- required primitive implementations,
- compatible Verilator version.

Bender remains Fledge's primary dependency manager.

Before choosing the final build mechanism, Phase 7 must perform a compile-only
dependency spike that answers:

1. Can Bender fetch and expose the pinned Ibex checkout reproducibly?
2. Can the required Ibex RTL source set be expressed cleanly in Fledge?
3. Is FuseSoC required to generate or collect any selected sources?
4. Can Verilator compile the selected configuration in the existing container?
5. Which upstream Python dependencies are required?
6. Can the dependency build run without modifying files inside the checkout?

Ibex's own flow uses FuseSoC metadata. Fledge may use FuseSoC for the Ibex
compilation unit if duplicating the upstream source list would be fragile.

Do not maintain permanent paths into hashed `.bender/` checkout directories.
Do not copy external Ibex RTL into Fledge-owned IP directories.

## SoC Structure

The initial CPU-enabled system will use separate instruction and data paths:

```text
                         +----------------+
                         |   ibex_top     |
                         +------+---+-----+
                                |   |
                       instruction data
                                |   |
                 +--------------+   +----------------+
                 |                                   |
          +------v------+                     +------v------+
          | instruction |                     | data        |
          | decoder     |                     | decoder     |
          +------+------+                     +--+------+---+
                 |                              |      |
          +------v------------------------------v--+   |
          | dual-port simulation memory system    |   |
          +----------------------------------------+   |
                                                   +--v-----------+
                                                   | peripheral   |
                                                   | bus adapter  |
                                                   +------+-------+
                                                          |
                                                   +------v-------+
                                                   | GPIO/timer/  |
                                                   | UART cluster |
                                                   +--------------+
```

The CPU wrapper and interconnect belong under `hw/soc/`. The existing
`fledge_soc` CPU-less wrapper must remain independently testable during the
transition.

## System Bus Boundary

The Ibex instruction and data interfaces connect to the Fledge system bus
defined in `docs/system_bus.md`.

The bus supports request and grant, delayed response, byte enables, explicit
errors, and one outstanding transaction per master. SoC integration must not
assume that request grant and response happen in the same cycle.

## Instruction And Data Paths

The instruction path is read-only and initially routes to executable simulation
memory. Instruction fetches from peripheral or unmapped regions return an
error. The first implementation has no instruction cache.

The data path initially routes to:

- boot memory for read-only constant data,
- writable data memory,
- GPIO,
- timer,
- UART,
- a default error responder.

The data path must preserve Ibex byte enables. Writes to boot memory return an
error.

## Register-Bus Evolution

The Phase 5 register bus is too limited for direct CPU integration because it
has no byte enables, no explicit error response, and one-cycle completion
assumptions.

The preferred end state adds:

```text
reg_be_i[3:0]
reg_error_o
```

to the peripheral register interface.

During migration, a stateful adapter may connect the Fledge system bus to the
existing register bus. The adapter must never silently treat a partial write
as a full-word write.

Each peripheral specification and cocotb testbench must define supported access
widths, writable bytes, read-only register behavior, reserved-offset behavior,
and misaligned-access behavior.

## Initial Memory Map

The CPU-enabled simulation target extends the current map:

| Address range | Block | Behavior |
| --- | --- | --- |
| `0x0000_0000` - `0x0000_3FFF` | boot memory | 16 KiB, executable and data-readable |
| `0x1000_0000` - `0x1000_3FFF` | data memory | 16 KiB, readable and writable |
| `0x4000_0000` - `0x4000_0FFF` | GPIO | existing GPIO region |
| `0x4000_1000` - `0x4000_1FFF` | timer | existing timer region |
| `0x4000_2000` - `0x4000_2FFF` | UART | existing UART region |

Memory sizes are initial simulation choices, not final implementation sizes.
Before implementing memory, update `docs/memory_map.md` and
`hw/soc/memory_map.yml` together.

## Boot Behavior

Ibex begins execution at `boot_addr_i + 0x80`. The initial system will drive:

```text
boot_addr_i = 0x0000_0000
```

Therefore the reset entry must be linked at `0x0000_0080`. The region below
the reset entry is reserved for future boot metadata or vectors. Simulation
must check the reset address rather than assuming it from the linker script.

## Memory Models

The first simulation memory system should provide:

- an instruction read port,
- a data read/write port,
- byte-enabled data writes,
- configurable response latency,
- initialization from a generated memory image,
- explicit errors for invalid accesses.

A zero-latency-only model is insufficient because it would not verify the
request/grant/response protocol. Synthesizable SRAM or ROM macros are deferred.

## Interrupt And Debug Policy

All interrupts are tied inactive for the first firmware-running milestone. The
existing timer completion output is not connected to Ibex until polling
firmware works. A later milestone may connect the timer to `irq_timer_i` and
document its clear and acknowledgment behavior.

The first integration does not instantiate a RISC-V debug module. Tie the Ibex
debug request inactive and disable debug triggers. JTAG and a debug module are
later infrastructure milestones.

## Software Timing

Do not add `sw/` during Phase 6. Add it when Ibex compiles in the Fledge
environment, the CPU wrapper exists, simulation memory can load an image, and
the linker memory map is agreed.

The initial software structure should be:

```text
sw/
  common/
    crt0.S
    link.ld
    fledge.h
  tests/
    smoke/
      main.c
      Makefile
```

Initial firmware should:

1. enter at `0x0000_0080`,
2. initialize the stack in data memory,
3. initialize `.data`,
4. clear `.bss`,
5. write a known GPIO value and enable GPIO output,
6. configure and poll the timer,
7. transmit a known UART byte,
8. write a completion signature,
9. enter a known loop.

The development container must pin or document the RISC-V compiler used by CI.

## Verification Layers

The existing block-level and CPU-less SoC tests remain required. Any intentional
change in unmapped-access semantics must update documentation and tests together.

Independent system-bus tests must cover delayed grant, delayed response, error
response, byte writes, stable request fields, one response per grant, no
response without a grant, reset behavior, and finite timeouts.

Memory tests must cover instruction and data reads, full-word and byte writes,
read-only boot-memory errors, invalid addresses, configurable response latency,
and image initialization.

The first CPU-level smoke test must check:

- the first fetch is from `0x0000_0080`,
- firmware reaches GPIO,
- firmware reaches the timer,
- firmware transmits the expected UART byte,
- firmware produces a completion signature,
- execution finishes within a finite timeout.

Fledge does not reproduce Ibex's complete upstream DV environment. Instead it
pins a reviewed revision, uses a supported named configuration, retains license
and revision information, and runs focused Fledge integration tests.

## Phase 7 Implementation Sequence

Phase 7 should use small reviewable changes:

1. Pin Ibex and prove that `ibex_top` compiles without SoC behavior changes.
2. Add reusable cocotb system-bus helpers and a controllable responder.
3. Implement and verify dual-port simulation memory.
4. Add byte enables and error behavior to the peripheral path.
5. Implement instruction and data decoding with a default error responder.
6. Instantiate Ibex `small`, apply explicit tie-offs, and test the first fetch.
7. Add the compiler, startup code, linker script, and firmware image flow.
8. Run firmware through Ibex and add the CPU smoke test to `make check`.

## Deferred Features

The first firmware-running milestone does not include instruction cache, PMP,
debug/JTAG, interrupts, SecureIbex, lockstep, branch prediction, production
memory macros, FPGA support, DMA, multiple bus masters, multiple outstanding
transactions, cache coherency, or physical-design integration.

These features are deferred, not rejected.

## Phase 6 Exit Criteria

Phase 6 is complete when:

- Ibex is selected as the first CPU,
- the supported initial configuration is identified,
- the system-bus protocol is documented,
- instruction and data paths are defined,
- memory and boot behavior are defined,
- dependency handling questions are recorded,
- software timing is decided,
- verification layers are defined,
- the Phase 7 implementation sequence is documented,
- the existing `make check` regression passes.

Phase 6 does not import or wire Ibex RTL.
