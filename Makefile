.PHONY: deps test test-example test-gpio lint lint-example lint-gpio clean 

deps:
	bender update
	bender checkout

check: check-ip-structure lint test

check-ip-structure:
	scripts/ip/check_ip_structure.py

test: test-example test-gpio test-timer test-uart

test-example:
	cd hw/ip/example_counter/dv && make

test-gpio:
	cd hw/ip/gpio/dv && make

test-timer:
	cd hw/ip/timer/dv && make

test-uart:
	cd hw/ip/uart/dv && make

lint: lint-example lint-gpio lint-timer lint-uart

lint-example:
	verilator --lint-only hw/ip/example_counter/rtl/counter.sv

lint-gpio:
	verilator --lint-only hw/ip/gpio/rtl/gpio.sv

lint-timer:
	verilator --lint-only hw/ip/timer/rtl/timer.sv

lint-uart:
	verilator --lint-only hw/ip/uart/rtl/uart.sv

clean:
	rm -rf hw/ip/example_counter/dv/sim_build
	rm -f hw/ip/example_counter/dv/results.xml
	rm -rf hw/ip/gpio/dv/sim_build
	rm -f hw/ip/gpio/dv/results.xml
	rm -rf hw/ip/timer/dv/sim_build
	rm -f hw/ip/timer/dv/results.xml
	rm -rf hw/ip/uart/dv/sim_build
	rm -f hw/ip/uart/dv/results.xml
