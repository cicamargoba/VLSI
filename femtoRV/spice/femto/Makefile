########################################################################################################
##########     !!!!  IMPORTANTE     !!!!!                                                          #####
#             XYCE NO SOPORTA LEVEL 3                                                              #####
# Se debe modificar el archivo:                                                                       #
# /usr/local/share/pdk/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__diode_pw2nd_05v5.model.spice #
# colocando un comentario en la línea:                                                                #
# *+ level = 3.0                                                                                      #
########################################################################################################
########################################################################################################


TARGET=femto
TOP=femto
NPROC=3

OBJS = femto.v
PER_OBJS =      perip_mult.v $(OBJS)
SIM_OBJS =      ../../cores/sim_spi_flash/spiflash.v
SIM_OBJS +=     ../../cores/sim_spi_ram/spiram.v
SIM_OBJS_SKY =  ../verilog_model/sky130_fd_sc_hd.v
SIM_OBJS_SKY += ../verilog_model/primitives.v


BUILD_DIR = build

all: sim

sim:
	rm -f a.out *.vcd
	iverilog -DFUNCTIONAL -DUNIT_DELAY=#1  $(TARGET)_TB.v $(OBJS) ${SIM_OBJS} ${SIM_OBJS_SKY}	
	vvp a.out
	gtkwave $(TARGET)_TB.vcd $(TARGET)_TB.gtkw

spice:
	ngspice ${TARGET}.spice
	python plot_${TARGET}.py


xyce:
	mpirun -np ${NPROC} Xyce ${TARGET}.cir
	python plot_${TARGET}.py


xyce_w_c:
	mpirun -np ${NPROC} Xyce ${TARGET}_w_c.cir
	python plot_${TARGET}.py

xyce_tim:
	python3 ../tim_to_pwl.py Mult_4.tim
	mpirun -np ${NPROC} Xyce ${TARGET}.cir
	python plot_${TARGET}.py


clean:
	rm -rf *.out *.vcd *.svg *.json *.raw
