# IP Checklist

Use this checklist for every reusable block under `hw/ip/<name>/`. It is
intentionally small: the goal is to make new IP easy to review without
pretending this repo is already a large silicon program.

## Required before merge

- [ ] `doc/README.md` explains purpose, owner, status, ports, reset behavior,
      and verification plan.
- [ ] `rtl/` contains synthesizable SystemVerilog only.
- [ ] `dv/` contains at least one self-checking testbench.
- [ ] The IP is reachable from the root `Makefile`.
- [ ] `make lint` passes in the toolchain container.
- [ ] `make test` passes in the toolchain container.
- [ ] Generated simulation artifacts are not committed.

## Design review

- [ ] Clock and reset polarity match repo convention: `clk_i`, active-low
      reset `rst_ni`.
- [ ] Inputs and outputs use `_i` and `_o` suffixes.
- [ ] Reset values are documented and tested.
- [ ] Control/status behavior is documented before implementation.
- [ ] Any open-source dependency is declared in `Bender.yml`, not copied into
      the tree casually.
- [ ] If the IP exposes a bus/register interface, the address map and register
      behavior are documented.

## Verification review

- [ ] Reset behavior is tested.
- [ ] Nominal behavior is tested.
- [ ] At least one disabled/idle/hold behavior is tested where applicable.
- [ ] Boundary values are tested where applicable.
- [ ] Tests are deterministic and self-checking.
- [ ] A known bug or subtle timing lesson is documented if the IP teaches one.

## Integration readiness

- [ ] The IP has no hidden dependency on simulation-only files.
- [ ] Parameters have sane defaults.
- [ ] Unused outputs are intentional and documented.
- [ ] The IP can be instantiated from a future `hw/soc` wrapper without
      changing its core behavior.