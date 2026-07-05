# Collaboration Guide

Fledge is intended to grow from a personal project into a collaborative
chip-design platform. Contributions should be small, reviewable, tested, and
connected to the architecture roadmap.

## Contribution Tracks

- **IP development:** reusable RTL blocks under `hw/ip/`
- **Verification:** cocotb tests, regression coverage, edge cases
- **SoC integration:** wrappers, memory maps, interconnect, `hw/soc/`
- **Infrastructure:** Docker, Makefile, Bender, CI, scripts
- **Firmware:** bare-metal programs, linker scripts, bring-up tests
- **Physical design:** OpenLane/OpenROAD flows, reports, constraints

## Workflow

1. Open or claim an issue.

2. Create a branch:

   ```bash
   git checkout -b feat/short-name
   ```

3. Edit on the host machine.

4. Run checks in the container:

   ```bash
   cd infra
   docker compose run --rm --pull never fledge-dev bash -c 'make lint && make test'
   ```

5. Commit from the host.

6. Open a pull request.

7. Merge only after CI passes and review is complete.

## Definition Of Done

For IP work:

- `rtl/`, `dv/`, and `doc/` exist.
- The IP is documented.
- The IP is included in the root `Makefile`.
- Lint passes.
- Tests pass.
- Generated files are not committed.
- The PR explains what changed and how it was tested.

For documentation or infrastructure work:

- The change is scoped and reviewable.
- Commands in docs are tested where practical.
- CI still passes.
