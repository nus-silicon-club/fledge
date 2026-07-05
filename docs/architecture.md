# Fledge Architecture

## Product Definition

Fledge is a tiny educational RISC-V microcontroller-class SoC. Its purpose is
to provide a practical collaboration platform for learning RTL design,
verification, SoC integration, firmware bring-up, FPGA prototyping, and
open-source physical design.

Fledge v0 is intentionally small, but its IP, verification, and integration
boundaries are chosen so the design can grow from an educational MCU into a
larger reusable SoC platform.

## Non-Goals

Fledge is not initially intended to be a Linux-capable SoC.

Fledge is not intended to compete with production microcontrollers.

Fledge is not initially intended to implement a custom CPU core from scratch.

Fledge is not a direct clone of OpenTitan, PULP, Ibex, Croc, or any single
open-source chip project.

## v0 Target

The v0 target is a minimal SoC that can run a bare-metal program which:

- boots from a simple memory model or ROM,
- configures GPIO,
- uses a timer,
- sends bytes over UART.

## Candidate Block Diagram

```text
        +----------------+
        | RV32 CPU Core  |
        +--------+-------+
                 |
                 | instruction/data bus
                 |
        +--------v-------+
        | Interconnect   |
        +--+------+------+------+
           |      |      |      |
        +--v--+ +-v--+ +-v--+ +-v---+
        | ROM | |RAM | |GPIO| |UART |
        +-----+ +----+ +----+ +-----+
                         |
                      +--v--+
                      |Timer|
                      +-----+
```

## Initial IP Blocks

- `gpio`: memory-mapped GPIO controller
- `timer`: simple counter/compare timer
- `uart`: serial TX/RX peripheral
- `soc`: integration wrapper and memory map

## Scaling Direction

Fledge should start as a tiny MCU, but the architecture should not trap the
project at that size. Future versions may add richer interconnect, larger
memory systems, DMA, accelerators, FPGA targets, or more capable RISC-V cores.

The scalable boundary is:

- reusable IP blocks under `hw/ip/`,
- bus/protocol wrappers separate from IP internals,
- documented memory maps,
- scripted verification and CI,
- dependency management through Bender,
- integration logic under `hw/soc/`.

## Bus Direction

Fledge should keep IP internals simple and bus-neutral where possible.

Early IP blocks may use a small internal register interface first. Bus-specific
protocols such as OBI, APB, or AXI-Lite should be added through wrappers or
generated register-interface logic once the project has enough peripherals to
justify the extra structure.

Croc/PULP use OBI heavily, so OBI compatibility is a future integration goal.
That does not mean every beginner IP should directly speak OBI from day one.

## Open-Source Leverage

Fledge should reuse mature open-source infrastructure where appropriate:

- Bender for dependency management,
- PULP `common_cells` for reusable RTL primitives,
- PULP/Croc as SoC architecture references,
- Ibex or another small RV32 core later,
- OpenLane/OpenROAD for physical-design experiments,
- cocotb and Verilator for verification.

Fledge should write small educational/integration IP itself, while reusing
mature infrastructure IP where bugs would be expensive or distracting.

## FPGA Direction

FPGA prototyping is a future milestone, not an immediate blocker.

A meaningful FPGA prototype should include a tiny SoC, firmware, GPIO mapped to
board LEDs/switches, and UART mapped to a serial interface. FPGA support should
come after GPIO, timer, UART, and a basic SoC simulation exist.

## v0 Success Criteria

- All IP blocks have `rtl/`, `dv/`, and `doc/`.
- CI runs lint and simulation regression through the root `Makefile`.
- `gpio`, `timer`, and `uart` pass block-level tests.
- A minimal SoC-level simulation exists.
- A bare-metal program can exercise GPIO/timer/UART.
- At least one block has passed an OpenLane smoke flow.
