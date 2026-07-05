.PHONY: deps test test-example test-gpio lint lint-example lint-gpio clean 

deps:
	bender update
	bender checkout

test: test-example test-gpio

test-example:
	cd hw/ip/example_counter/dv && make

test-gpio:
	cd hw/ip/gpio/dv && make

lint: lint-example lint-gpio

lint-example:
	verilator --lint-only hw/ip/example_counter/rtl/counter.sv

lint-gpio:
	verilator --lint-only hw/ip/gpio/rtl/gpio.sv

clean:
	rm -rf hw/ip/example_counter/dv/sim_build
	rm -f hw/ip/example_counter/dv/results.xml
	rm -rf hw/ip/gpio/dv/sim_build
	rm -f hw/ip/gpio/dv/results.xml
