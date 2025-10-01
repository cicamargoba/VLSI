import ltspice
import matplotlib
#matplotlib.use("TkAgg")  # o "Qt5Agg" si tienes Qt
import matplotlib.pyplot as plt
import numpy as np
import os
#from scipy import signal

filepath='/Work/VLSI/VLSI/femtoRV/spice/femto/femto.raw'
l=ltspice.Ltspice(filepath)
l.parse() # Data loading sequence. It may take few minutes for huge file.

print("Variables disponibles en el archivo:")
print(l.variables)

time=l.get_time()
V1=l.get_data('V(CLK)')
V2=l.get_data('V(RESETN)')
V3=l.get_data('V(SPI_MISO)')
V4=l.get_data('V(SPI_MISO_RAM)')
V5=l.get_data('V(_06574)')
#V6=l.get_data('V(SPI_MOSI_RAM)')

signals = [V1, V2, V3, V4, V5]
sig_names = ["clk", "rst", "spi_miso", "spi_miso_ram", "spi_mosi", "spi_mosi_ram"]

# Create stacked subplots
fig, axes = plt.subplots(15, 1, figsize=(12, 20), sharex=True)

for i, (ax, sig) in enumerate(zip(axes, signals)):
    ax.plot(time, sig, color=plt.cm.viridis(i/15), linewidth=1)  # Color gradient
    ax.set_ylabel(sig_names[i], rotation=0, ha='right', va='center')
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.5, 3.5)

axes[-1].set_xlabel('Time (s)')
plt.suptitle('17 Signals (Stacked Subplots)', y=0.92)
plt.tight_layout()
plt.show()



plt.plot(time, V1, label = "clk")
plt.plot(time, V2+4)
plt.plot(time, V3+8)
plt.plot(time, V4+12)
plt.plot(time, V5+16)
plt.plot(time, V6+20)
plt.plot(time, V7+24)
plt.plot(time, V8+28)
plt.plot(time, V9+32)
plt.plot(time, V10+36)
plt.plot(time, V11+40)
plt.plot(time, V12+44)
plt.plot(time, V13+48)
plt.plot(time, V14+52)
plt.plot(time, V15+56)
plt.plot(time, V16+60)
plt.plot(time, V17+64)
plt.plot(time, V18+70)
plt.plot(time, V19+74)
plt.legend()
plt.grid()
plt.show()


