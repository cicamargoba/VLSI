# Suite de verificación femto_UN  (RTL = commit f15fccd, el silicio fabricado)
#   make unit | integration | functional | e2e | acceptance | all
#   MEM_PROFILE=standard (memorias SPI estándar, por defecto) | silicon_aware (workaround)
SRC      ?= $(abspath $(CURDIR)/../src)
PROFILE  ?= $(or $(MEM_PROFILE),standard)
export PATH := $(HOME)/opt/iverilog-12/bin:$(PATH)
export MEM_PROFILE := $(PROFILE)
export PYTHONPATH  := $(CURDIR)/lib:$(CURDIR)/unit:$(CURDIR)/integration:$(CURDIR)/functional:$(CURDIR)/e2e:$(CURDIR)/acceptance:$(CURDIR)/hw:$(CURDIR)/tools
SOC_SRC  = $(SRC)/femto.v $(SRC)/femtorv32_quark.v $(SRC)/perip_uart.v $(SRC)/uart.v $(SRC)/MappedSPIFlash.v $(SRC)/MappedSPIRAM.v
RES      = $(CURDIR)/results/$(PROFILE)

# $(call RUN,nombre,toplevel,modulo,fuentes,args-extra)
define RUN
@mkdir -p $(RES)
SIM_BUILD=sim_build/$(1) TOPLEVEL=$(2) COCOTB_TEST_MODULES=$(3) VERILOG_SOURCES="$(4)" \
  COMPILE_ARGS="$(5)" COCOTB_RESULTS_FILE=$(RES)/$(1).xml $(MAKE) -f Makefile.sim || true
endef

.PHONY: hw hwdbg flashdbg all unit unit-quark unit-spiram unit-spiflash unit-uart integration functional e2e acceptance clean report
all: unit integration functional e2e acceptance report

unit: unit-quark unit-spiram unit-spiflash unit-uart
unit-quark:    ; $(call RUN,unit_quark,FemtoRV32,test_unit_quark,$(SRC)/femtorv32_quark.v,-DBENCH)
unit-spiram:   ; $(call RUN,unit_spiram,MappedSPIRAM,test_unit_spiram,$(SRC)/MappedSPIRAM.v,)
unit-spiflash: ; $(call RUN,unit_spiflash,MappedSPIFlash,test_unit_spiflash,$(SRC)/MappedSPIFlash.v,)
unit-uart:     ; $(call RUN,unit_uart,peripheral_uart,test_unit_uart,$(SRC)/perip_uart.v $(SRC)/uart.v,-Pperipheral_uart.clk_freq=27000000 -Pperipheral_uart.baud=115200)
integration:   ; $(call RUN,integration,tt_um_femto,test_integration,$(SOC_SRC),)
functional:    ; $(call RUN,functional,tt_um_femto,test_functional,$(SOC_SRC),)
e2e:           ; $(call RUN,e2e,tt_um_femto,test_e2e,$(SOC_SRC),)
acceptance:    ; $(call RUN,acceptance,tt_um_femto,test_acceptance,$(SOC_SRC),)
report:        ; python3 tools/report.py $(RES)
clean:         ; rm -rf sim_build __pycache__ */__pycache__ results

# utilidad de depuración:  make dbg MOD=explore_soc
dbg:           ; $(call RUN,dbg,tt_um_femto,$(MOD),$(SOC_SRC),)

# co-simulación con el emulador RTL (workaround de hardware)
hw:            ; $(call RUN,hw_emulator,tb_soc_emu,test_hw_emulator,$(SOC_SRC) $(CURDIR)/hw/silicon_spi_mem.v $(CURDIR)/hw/tb_soc_emu.v,)
hwdbg:         ; $(call RUN,hwdbg,tb_soc_emu,$(MOD),$(SOC_SRC) $(CURDIR)/hw/silicon_spi_mem.v $(CURDIR)/hw/tb_soc_emu.v,)
flashdbg:      ; $(call RUN,flashdbg,MappedSPIFlash,$(MOD),$(SRC)/MappedSPIFlash.v,)
