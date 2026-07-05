SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/../rtl/uart.sv
TOPLEVEL = uart
MODULE = test_uart

include $(shell cocotb-config --makefiles)/Makefile.sim
