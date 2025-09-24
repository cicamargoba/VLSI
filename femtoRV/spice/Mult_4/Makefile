TARGET=Mult_4
TOP=Mult_4
NPROC=4

OBJS = Mult_4.nl.v
PER_OBJS = perip_mult.v $(OBJS)
SIM_OBJS = cores/sim_spi_flash/spiflash.v
SIM_OBJS_SKY = ../verilog_model/sky130_fd_sc_hd.v
SIM_OBJS_SKY += ../verilog_model/primitives.v


BUILD_DIR = build

all: sim

sim:
	rm -f a.out *.vcd
	iverilog -DFUNCTIONAL -DUNIT_DELAY=#1  $(TARGET)_TB.v $(OBJS) ${SIM_OBJS_SKY}	
	vvp a.out
	gtkwave $(TARGET)_TB.vcd $(TARGET)_TB.gtkw

sim_per:
	rm -f a.out *.vcd
	iverilog  -DFUNCTIONAL -DUNIT_DELAY=#1  perip_$(TARGET)_TB.v $(PER_OBJS)
	vvp a.out
	gtkwave perip_$(TARGET)_TB.vcd 

spice:
	ngspice ${TARGET}.spice
	python plot_${TARGET}.py


xyce:
	mpirun -np ${NPROC} Xyce ${TARGET}_TB.cir
	python plot_${TARGET}.py

xyce_tim:
	python3 ../tim_to_pwl.py Mult_4.tim
	mpirun -np ${NPROC} Xyce ${TARGET}.cir
	python plot_${TARGET}.py


clean:
	rm -rf *.out *.vcd *.svg *.json *.raw
