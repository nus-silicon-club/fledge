# Onboarding

This repo uses a Docker-based development environment so contributors do not need to install Verilator, cocotb, Bender, or other hardware tools directly on their host machine.

## Host vs Container

Use your host Ubuntu environment for:

- editing files,
- Git operations,
- VS Code or another editor,
- browser/GitHub work.

Use the `fledge-dev` container for:

- `make lint`,
- `make test`,
- `bender update`,
- `bender checkout`,
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

4. Enter the development container:

   ```bash
   cd infra
   docker compose run --rm --pull never fledge-dev
   ```

5. Inside the container, verify the environment:

   ```bash
   cd /workspace
   make lint
   make test
   ```

   The current regression should run the reference counter and GPIO tests. If it fails, stop and fix the environment before starting new RTL work.

## Daily Workflow

From your host Ubuntu shell:

```bash
cd ~/chip-club-infra/chip-club-infra
git status
git checkout -b feat/my-change
```

Edit files on the host. Then run hardware checks inside the container:

```bash
cd infra
docker compose run --rm --pull never fledge-dev bash -c 'make lint && make test'
```

If checks pass, commit from the host:

```bash
cd ..
git add <files>
git commit -m 'short description'
git push
```

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