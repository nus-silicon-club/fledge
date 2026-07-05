SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/../rtl/gpio.sv
TOPLEVEL = gpio
MODULE = test_gpio

include $(shell cocotb-config --makefiles)/Makefile.sim
