# Onboarding

1. Install Docker.
2. `git clone` this repo.
3. Run `./infra/setup.sh` -- this pulls the shared toolchain image, or
   builds it locally if the published image is not available yet.
4. Enter the environment: `cd infra && docker compose run --rm --pull never fledge-dev`
5. Verify your environment works:
   ```
   cd hw/ip/example_counter/dv && make
   ```
   You should see `TESTS=3 PASS=3 FAIL=0`. If you don't, stop here and
   ask for help before moving on -- everything else builds on this working.
6. Read `hw/ip/example_counter/doc/README.md` in full, including the
   verification notes. It documents a real bug we hit building this
   exact example, and the lesson generalizes to almost every testbench
   you'll write.
7. Start with `curriculum/01-architecture`.

## Physical design (later, once you're past RTL + verification)
This repo's Docker image intentionally does not include OpenLane/OpenROAD --
that flow is large and versions quickly. Use the official OpenLane container
directly for `curriculum/05-physical-design` and beyond; instructions will be
added there as the club reaches that stage.
