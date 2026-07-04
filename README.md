# NUSilicon -- Front-End Chip Design

Front-end silicon design, engineering-focused: RTL design, verification,
integration, and physical design, built on open-source hardware tooling
(PULP, OpenLane/Sky130) toward a Tiny Tapeout submission.

## Repo structure

```
.
├── hw/
│   ├── ip/                        # club-original IP blocks
│   │   └── example_counter/       # reference IP -- copy this pattern
│   │       ├── rtl/               #   design sources
│   │       ├── dv/                #   testbench (cocotb)
│   │       └── doc/               #   spec + status + verification notes
│   └── soc/                       # integration layer
│       ├── rtl/                   #   vendored external IPs land here as
│       │                          #   rtl/<ip_name>, PULP/Croc-style, plus
│       │                          #   top-level integration wrappers
│       └── dv/                    #   platform-level testbench
│
├── vendor/                        # raw upstream checkouts (Bender/FuseSoC managed)
│
├── curriculum/                    # one module per flow stage, staged capstones
│   ├── 01-architecture/
│   ├── 02-rtl/
│   ├── 03-verification/
│   ├── 04-integration/
│   ├── 05-physical-design/
│   └── 06-dft-signoff/
│
├── infra/                         # environment: Dockerfile, compose, setup.sh
├── docs/                          # onboarding, tool guides, governance
├── .github/workflows/ci.yml       # regression on every PR
└── LICENSE                        # Apache-2.0 / Solderpad (matches PULP ecosystem)
```

### Why the IP layer and SoC layer look different
`hw/ip/<name>/{rtl,dv,doc}` -- the IP name is the parent, disciplines are
children. This matches OpenTitan's convention for a single IP's own repo:
design/verification/docs are different disciplines within one block.

`hw/soc/rtl/<ip_name>` -- at the integration layer, `rtl` is the parent
and each vendored IP is a child. This is what PULP's own repos do when
composing a full chip (see `croc`, PULP's education-focused SoC that
taped out on IHP's open PDK) -- verification and docs at this layer
apply to the whole platform, not to any single vendored IP.

## Toolchain
See `infra/Dockerfile`. Validated combination: Verilator 5.020 (Ubuntu
24.04 apt) + cocotb 1.9.x. Physical design (OpenLane/OpenROAD + Sky130)
runs via the official OpenLane container, not this image -- see
`docs/onboarding.md`.

## Getting started
See `docs/onboarding.md`.

## Open-source dependencies this club builds on
PULP / Ibex / CVA6 (starter cores and peripherals), FuseSoC / Bender
(dependency management), Verilator / cocotb (simulation + verification),
OpenLane / OpenROAD (synthesis, place & route, STA), Sky130 (PDK),
Tiny Tapeout (fabrication target), OpenTitan (verification methodology
reference), CHIPS Alliance (umbrella tooling/standards).
