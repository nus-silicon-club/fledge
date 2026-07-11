# Onboarding

This repo uses a Docker-based development environment so contributors do not need to install Verilator, cocotb, Bender, or other hardware tools directly on their host machine.

## Host vs Container

Use your host Ubuntu environment for:

- editing files,
- Git operations,
- VS Code or another editor,
- browser/GitHub work.

Use the `fledge-dev` container for:

- `make check`,
- `make lint`,
- `make test`,
- `make lint-ibex`,
- future EDA scripts and checks.

## First-Time Setup

1. Install Docker.
2. Clone the repo:

   ```bash
   git clone https://github.com/nus-silicon-club/fledge.git
   cd fledge
   ```

3. Pull or build the shared toolchain image:

   ```bash
   ./infra/setup.sh
   ```

4. From the repository root, enter the development container:

   ```bash
   make shell
   ```

5. Inside the container, verify the environment:

   ```bash
   make check
   ```

   This fetches pinned external dependencies, then runs structure checks, RTL
   lint, Ibex lint, block-level tests, and SoC-level tests. If it fails, stop
   and fix the environment before starting new RTL work.

## Daily Workflow

From your host Ubuntu shell:

```bash
cd ~/chip-club-infra/chip-club-infra
git status
git switch -c feat/my-change
```

Edit files on the host. Run the complete dependency setup and regression with:

```bash
make check
```

If checks pass, commit from the host:

```bash
git add <files>
git commit -m 'short description'
git push
```

For an interactive hardware-tools session instead, run `make shell`, then use
`make check` or individual lint and test targets inside the container. Type
`exit` to return to the host shell.

## What To Read First

1. `docs/architecture.md` for the Fledge v0 target.
2. `docs/ip_checklist.md` for the definition of done for IP blocks.
3. `hw/ip/example_counter/doc/README.md` for the reference IP pattern.
4. `hw/ip/gpio/doc/README.md` for the first real peripheral example.
5. `curriculum/01-architecture` once the curriculum track is filled in.

## Generated Files

Simulation outputs such as `sim_build/` and `results.xml` are generated files and should not be committed. If in doubt, run:

```bash
git status --ignored
```

## Physical Design

This repo's main Docker image intentionally focuses on frontend RTL work for now. OpenLane/OpenROAD support will be added later as a separate physical-design smoke flow for small blocks such as `gpio` or `timer`.
