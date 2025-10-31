TARGET=femto
TOP=femto
OPENLANE_SYNT=/media/carlos/Work/VLSI/OpenLane/designs/femto/runs/full_guide/results/synthesis
OPENLANE_TOP=femto
SKY_LIB_TECH=$(HOME)/.volare/sky130A/libs.tech/openlane/

OBJS = OpenLane/src/femto.v
OBJS+= OpenLane/src/femtorv32_quark.v
OBJS+= OpenLane/src/perip_uart.v
OBJS+= OpenLane/src/uart.v
OBJS+= OpenLane/src/perip_mult.v
OBJS+= OpenLane/src/mult.v
OBJS+= OpenLane/src/bram.v
OBJS+= OpenLane/src/MappedSPIFlash.v
OBJS+= OpenLane/src/MappedSPIRAM.v

//OBJS+= cores/spi_flash/MappedSPIFlash.v
SIM_OBJS = cores/sim_spi_flash/spiflash.v
SIM_OBJS+= cores/sim_spi_ram/spiram.v
SIM_OBJS_SKY = verilog_model/sky130_fd_sc_hd.v
SIM_OBJS_SKY += verilog_model/primitives.v

BUILD_DIR = build

all: $(TARGET).fs

$(TARGET).fs: 
	gw_sh  soc_flash_src.tcl

${TARGET}.svf : ${TARGET}.bit

sim: 
	rm -f a.out *.vcd
	iverilog -DBENCH -DSIM -DPASSTHROUGH_PLL -DBOARD_FREQ=27 -DCPU_FREQ=27 $(TOP)_TB.v ${OBJS} ${SIM_OBJS}
	vvp a.out
	gtkwave bench.vcd
#conda install -c conda-forge click
# o sudo pip3 install Click

prepare_libs:
	#rm -rf tmp synthesis
	mkdir -p synthesis
	mkdir -p tmp/routing
	mkdir -p tmp/synthesis/blackbox
	mkdir -p tmp/cts
	mkdir -p logs/synthesis/
	mkdir -p synthesis/blackbox/
	rm -rf tmp/synthesis/*.list  tmp/cts/*

#	scripts/openroad -exit -no_init -python scripts/odbpy/lefutil.py get_metal_layers -o tmp/layers.list $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
	scripts/mergeLef.py -o tmp/merged.nom.lef -i $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_ef_sc_hd.lef
	scripts/mergeLef.py -o tmp/merged.min.lef -i $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__min.tlef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_ef_sc_hd.lef
	scripts/mergeLef.py -o tmp/merged.max.lef -i $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__max.tlef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_ef_sc_hd.lef
	scripts/mergeLib.py --output tmp/synthesis/merged.lib --name sky130A_merged $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
	cat ${SKY_LIB_TECH}/sky130_fd_sc_hd/drc_exclude.cells ${SKY_LIB_TECH}/sky130_fd_sc_hd/no_synth.cells > tmp/synthesis/trimmed.lib.exclude.list
	scripts/libtrim.py --cell-file tmp/synthesis/trimmed.lib.exclude.list --output tmp/synthesis/trimmed.lib tmp/synthesis/merged.lib
	cat ${SKY_LIB_TECH}/sky130_fd_sc_hd/drc_exclude.cells > tmp/cts/cts.lib.exclude.list
	scripts/libtrim.py --cell-file tmp/cts/cts.lib.exclude.list --output tmp/cts/cts.lib $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
	cat ${SKY_LIB_TECH}/sky130_fd_sc_hd/drc_exclude.cells > tmp/cts/cts-fastest.lib.exclude.list
	scripts/libtrim.py --cell-file tmp/cts/cts-fastest.lib.exclude.list --output tmp/cts/cts-fastest.lib $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ff_n40C_1v95.lib
	cat ${SKY_LIB_TECH}/sky130_fd_sc_hd/drc_exclude.cells > tmp/cts/cts-slowest.lib.exclude.list
	scripts/libtrim.py --cell-file tmp/cts/cts-slowest.lib.exclude.list --output tmp/cts/cts-slowest.lib $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib
	scripts/new_tracks.py -i $(HOME)/.volare/sky130A/libs.tech/openlane/sky130_fd_sc_hd/tracks.info -o tmp/routing/config.tracks
	cp $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd__blackbox.v  synthesis/blackbox/
	yosys -c scripts/yosys/blackbox.tcl
	@verilator -Wall --lint-only --Wno-DECLFILENAME --top-module ${TARGET} synthesis/blackbox/sky130_fd_sc_hd__blackbox.v ${OBJS}  -Wno-fatal --relative-includes | tee -i logs/synthesis/linter.log /dev/null
	sed -E 's/^([[:space:]]+)pg_pin(.*)/\1pin\2\n\1    direction : "inout";/g' $(HOME)/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib > tmp/synthesis/1-sky130_fd_sc_hd__tt_025C_1v80.no_pg.lib
	sed -E 's/^([[:space:]]+)pg_pin(.*)/\1pin\2\n\1    direction : "inout";/g' ./synthesis/trimmed.lib > ./synthesis/1-trimmed.no_pg.lib
	yosys -c scripts/yosys/synth.tcl 
	cp out.v ${TARGET}_sky.v
#	cp tmp/synthesis/trimmed.lib ./synthesis/
sim_post_syn_sky: prepare_libs
	iverilog -DFUNCTIONAL -DUNIT_DELAY=#1  -o $@_PS.vpp -s $(TOP)_TB $(TARGET)_TB.v ${TARGET}_sky.v ${SIM_OBJS} ${SIM_OBJS_SKY}
	vvp $@_PS.vpp
	./$@_PS.vpp
	gtkwave $(TOP)_TB.vcd &
	#netlistsvg ${TARGET}.json -o ${TARGET}.svg  #--skin default.svg
run_opensta:
	sta -exit -no_init multi_corner.tcl |& tee  ./synthesis/2-sta.log
#"sta -exit -no_init /openlane/scripts/openroad/sta/multi_corner.tcl |& tee /dev/null /openlane/designs/Mult_4/runs/RUN_2025.05.21_13.33.51/logs/synthesis/2-sta.log"

## ---------------------
## post-synth simulation
## ---------------------
$(TOP).json:
	yosys -v3 -l synth.log -p 'setattr -set keep 1 ; synth -flatten; synth_ecp5 -top SOC_flash -json $(TOP).json; write_verilog -attr2comment $(TOP)_synth.v' ${OBJS}
#	yosys -v3 -l synth.log -p 'synth_ecp5 -top SOC_flash -json $(TOP).json; write_verilog -attr2comment $(TOP)_synth.v' ${OBJS}

 
femto:
	cp ${OPENLANE_SYNT}/${OPENLANE_TOP}.v .
	iverilog -DFUNCTIONAL -DUNIT_DELAY=#1  -o ${OPENLANE_TOP}.vpp -s ${OPENLANE_TOP}_TB ${OPENLANE_TOP}_TB.v ${OPENLANE_TOP}.v cores/sim_spi_flash/spiflash.v cores/sim_spi_ram/spiram.v verilog_model/sky130_fd_sc_hd.v verilog_model/primitives.v
	vvp ${OPENLANE_TOP}.vpp
	./${OPENLANE_TOP}.vpp
	gtkwave ${OPENLANE_TOP}_TB.vcd &	
svg: $(OBJS)
	yosys -p "prep -top ${TARGET}; write_json ${TARGET}.json" -DPASSTHROUGH_PLL -DBOARD_FREQ=27 -DCPU_FREQ=27  ${OBJS}
	netlistsvg ${TARGET}.json -o ${TARGET}.svg  #--skin default.svg
	yosys -p "prep -top ${TARGET} -flatten; write_json ${TARGET}_flat.json" ${OBJS}
	netlistsvg ${TARGET}_flat.json -o ${TARGET}_flat.svg  #--skin default.svg


clean:
	rm -rf impl obj_dir *svg a.out *.vcd *.json *.bit build *.vpp *.log SOC_flash_synth_sky SOC_flash_synth_sky.v ${OPENLANE_TOP}.v

configure: ${TARGET}.fs
	sudo openFPGALoader -b tangprimer20k -m impl/pnr/project.fs

# export PATH=$PATH:$(HOME)/Embedded/Gowin/IDE/bin
#Install netlistsvg for svg generation
