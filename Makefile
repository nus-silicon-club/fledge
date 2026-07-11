.PHONY: shell deps check check-local check-ip-structure check-memory-map test test-example test-gpio test-timer test-uart test-soc test-memory-map lint lint-example lint-gpio lint-timer lint-uart lint-soc lint-ibex clean

shell:
	docker compose -f infra/docker-compose.yml run --rm --pull never fledge-dev

deps:
	bender checkout
	bender vendor init

ifeq ($(FLEDGE_IN_CONTAINER),1)
check: deps check-local
else
check:
	docker compose -f infra/docker-compose.yml run --rm --pull never \
		fledge-dev make check
endif

check-local: check-ip-structure check-memory-map lint test 

check-ip-structure:
	scripts/ip/check_ip_structure.py

check-memory-map:
	scripts/soc/check_memory_map.py hw/soc/memory_map.yml

test: test-example test-gpio test-timer test-uart test-soc test-memory-map

test-example:
	cd hw/ip/example_counter/dv && make

test-gpio:
	cd hw/ip/gpio/dv && make

test-timer:
	cd hw/ip/timer/dv && make

test-uart:
	cd hw/ip/uart/dv && make

test-soc:
	cd hw/soc/dv && make

test-memory-map:
	pytest -q scripts/soc/test_check_memory_map.py

lint: lint-example lint-gpio lint-timer lint-uart lint-soc lint-ibex

lint-example:
	verilator --lint-only hw/ip/example_counter/rtl/counter.sv

lint-gpio:
	verilator --lint-only hw/ip/gpio/rtl/gpio.sv

lint-timer:
	verilator --lint-only hw/ip/timer/rtl/timer.sv

lint-uart:
	verilator --lint-only hw/ip/uart/rtl/uart.sv

lint-soc:
	verilator --lint-only \
		hw/ip/gpio/rtl/gpio.sv \
		hw/ip/timer/rtl/timer.sv \
		hw/ip/uart/rtl/uart.sv \
		hw/soc/rtl/fledge_soc.sv

lint-ibex:
	fusesoc \
		--cores-root=vendor/ibex \
		--cores-root=hw/soc/ibex \
		run \
		--target=lint \
		--build-root=build/ibex \
		fledge:integration:ibex

clean:
	rm -rf hw/ip/example_counter/dv/sim_build
	rm -f hw/ip/example_counter/dv/results.xml
	rm -rf hw/ip/gpio/dv/sim_build
	rm -f hw/ip/gpio/dv/results.xml
	rm -rf hw/ip/timer/dv/sim_build
	rm -f hw/ip/timer/dv/results.xml
	rm -rf hw/ip/uart/dv/sim_build
	rm -f hw/ip/uart/dv/results.xml
	rm -rf hw/soc/dv/sim_build
	rm -f hw/soc/dv/results.xml
	rm -rf build/ibex
