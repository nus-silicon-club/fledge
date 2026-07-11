# Fledge

Fledge is a tiny educational RISC-V microcontroller-class SoC project. Its purpose is to become a practical collaboration platform for learning frontend chip design: RTL, verification, SoC integration, firmware bring-up, FPGA prototyping, and open-source physical design.

The project starts small on purpose. Fledge v0 aims to build a minimal MCU that can run bare-metal code, configure GPIO, use a timer, and send bytes over UART. The repo is structured so those early blocks can grow into a larger reusable SoC platform instead of becoming one-off coursework exercises.

## Current Status

Implemented:

- `example_counter`: reference IP used to teach the repo pattern.
- `gpio`: first bus/register-facing peripheral IP.
- Docker-based toolchain with Verilator, cocotb, and Bender.
- GitHub Actions regression through the root `Makefile`.
- Bender dependency metadata and lockfile.

Planned next:

- `timer`: counter/compare timer peripheral.
- `uart`: serial TX/RX peripheral.
- `hw/soc`: tiny SoC wrapper and memory map.
- OpenLane/OpenROAD smoke flow for small blocks.

## Repo Structure

```text
.
|-- hw/
|   |-- ip/                         # reusable IP blocks
|   |   |-- example_counter/         # reference IP
|   |   `-- gpio/                    # memory-mapped GPIO peripheral
|   |       |-- rtl/                 # design sources
|   |       |-- dv/                  # cocotb testbench
|   |       `-- doc/                 # spec, status, verification notes
|   `-- soc/                        # future SoC integration layer
|       |-- rtl/
|       `-- dv/
|
|-- vendor/                         # committed external snapshots only, if needed
|-- curriculum/                     # staged learning tracks and capstones
|-- infra/                          # Dockerfile, compose, setup script
|-- docs/                           # architecture, onboarding, checklists
|-- .github/workflows/ci.yml        # regression on push and PR
|-- Bender.yml                      # HDL package/dependency metadata
|-- Bender.lock                     # pinned dependency resolution
|-- Makefile                        # project command surface
`-- LICENSE
```

## Architecture

Read `docs/architecture.md` for the product definition and roadmap. In short:

- Fledge v0 is a tiny educational MCU.
- IP blocks should remain reusable and mostly bus-neutral internally.
- Bus-specific protocols such as OBI, APB, or AXI-Lite can be added through wrappers or generated register-interface logic later.
- PULP/Croc are architecture references, not folder trees to copy blindly.
- Open-source IP should be reused deliberately through Bender.

## Development Workflow

Use the host Ubuntu environment for editing and Git operations. Use the Docker container for hardware tools.

Typical flow:

```bash
cd infra
docker compose run --rm --pull never fledge-dev
```

Inside the container:

```bash
cd /workspace
make lint
make test
```

The root `Makefile` is the public command surface. CI runs the same checks that contributors run locally.

## Useful Docs

- `docs/onboarding.md`: first-time setup and local workflow.
- `docs/architecture.md`: what kind of chip Fledge is building.
- `docs/ip_checklist.md`: definition of done for reusable IP blocks.
- `docs/system_bus.md`: request/response bus for CPU and SoC integration.
- `docs/cpu_integration.md`: Phase 6 Ibex integration plan.

## Toolchain

The current development image focuses on frontend RTL work:

- Verilator for lint and simulation backend.
- cocotb for Python testbenches.
- Bender for HDL dependency management.
- PULP `common_cells` as the first open-source RTL dependency.

Physical design is intentionally separate for now. OpenLane/OpenROAD support will be added as a later smoke-flow milestone once the RTL platform is more settled.

## Open-Source Dependencies This Project Builds On

PULP / Ibex / Croc, Bender, Verilator, cocotb, OpenLane / OpenROAD, Sky130, Tiny Tapeout, OpenTitan, and CHIPS Alliance projects are reference points or future integration targets. Fledge should reuse mature infrastructure where it helps, while keeping the early educational SoC understandable.
