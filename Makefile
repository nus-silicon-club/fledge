.PHONY: deps check check-ip-structure test test-example test-gpio test-timer test-uart test-soc lint lint-example lint-gpio lint-timer lint-uart lint-soc  clean 

deps:
	bender update
	bender checkout

check: check-ip-structure lint test

check-ip-structure:
	scripts/ip/check_ip_structure.py

test: test-example test-gpio test-timer test-uart test-soc

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

lint: lint-example lint-gpio lint-timer lint-uart lint-soc

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
