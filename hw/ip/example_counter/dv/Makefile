SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/../rtl/counter.sv
TOPLEVEL = counter
MODULE = test_counter

include $(shell cocotb-config --makefiles)/Makefile.sim
