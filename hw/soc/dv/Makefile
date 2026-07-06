SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = \
  $(PWD)/../../ip/gpio/rtl/gpio.sv \
  $(PWD)/../../ip/timer/rtl/timer.sv \
  $(PWD)/../../ip/uart/rtl/uart.sv \
  $(PWD)/../rtl/fledge_soc.sv

TOPLEVEL = fledge_soc
MODULE = test_fledge_soc

include $(shell cocotb-config --makefiles)/Makefile.sim
