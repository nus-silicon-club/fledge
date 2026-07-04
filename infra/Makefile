.PHONY: deps test test-example lint clean

deps:
	bender update
	bender checkout

test: test-example

test-example:
	cd hw/ip/example_counter/dv && make

lint:
	verilator --lint-only -Wall hw/ip/example_counter/rtl/counter.sv

clean:
	rm -rf hw/ip/example_counter/dv/sim_build
	rm -f hw/ip/example_counter/dv/results.xml
