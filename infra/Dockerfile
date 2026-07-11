# Club RTL + verification toolchain.
# Physical design (OpenLane/OpenROAD) is deliberately NOT in this image --
# use the official OpenLane container for that stage (see README). Keeping
# the two separate makes this image fast to build and keeps the PD flow
# on whatever version OpenLane itself ships.
FROM ubuntu:24.04
LABEL org.opencontainers.image.source="https://github.com/nus-silicon-designers/fledge" \
      org.opencontainers.image.description="Fledge RTL and verification toolchain" \
      org.opencontainers.image.licenses="Apache-2.0"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git curl ca-certificates cmake \
        python3 python3-pip python3-venv python3-dev \
        verilator \
    && rm -rf /var/lib/apt/lists/*

# NOTE on versions (validated 4 Jul 2026):
# Ubuntu 24.04's apt Verilator is 5.020. cocotb 2.x requires Verilator
# >=5.036 and will refuse to run on 5.020. Rather than building Verilator
# from source (slow, adds build-time flakiness for a student club image),
# we pin cocotb to the 1.9.x line, which supports this Verilator cleanly.
# If you later rebuild Verilator from source at >=5.036, you can move to
# cocotb 2.x -- just re-test the example IP in hw/ip/example_counter first.
RUN pip3 install --break-system-packages --no-cache-dir \
        "cocotb<2.0" \
        "fusesoc==2.4.3" \
        "PyYAML==6.0.3" \
        pytest

# Rust + Bender, for PULP-style IP dependency management
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN cargo install bender

WORKDIR /workspace
CMD ["/bin/bash"]
