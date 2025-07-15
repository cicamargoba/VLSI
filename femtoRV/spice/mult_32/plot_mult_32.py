import ltspice
import matplotlib.pyplot as plt
import numpy as np
import os
#from scipy import signal

filepath='/Work/VLSI/VLSI/femtoRV/spice/mult_32/mult32_TB_cir.raw'
l=ltspice.Ltspice(filepath)
l.parse() # Data loading sequence. It may take few minutes for huge file.
time=l.get_time()
V1=l.get_data('V(clk)')
V2=l.get_data('v(rst)')
V3=l.get_data('v(init)')
V4=l.get_data('v(control0.sh)')
V5=l.get_data('v(control0.add)')
V6=l.get_data('v(A[0])')
V7=l.get_data('v(A[1])')
V8=l.get_data('v(A[2])')
V9=l.get_data('v(A[3])')
V10=l.get_data('v(A[7])')
V11=l.get_data('v(pp[0])')
V12=l.get_data('v(pp[1])')
V13=l.get_data('v(pp[2])')
V14=l.get_data('v(pp[3])')
V15=l.get_data('v(pp[4])')
V16=l.get_data('v(pp[5])')
V17=l.get_data('v(pp[6])')
V18=l.get_data('v(pp[7])')
V19=l.get_data('v(pp[8])')
V20=l.get_data('v(pp[9])')
V21=l.get_data('v(pp[10])')
V22=l.get_data('v(pp[11])')
V23=l.get_data('v(pp[12])')
V24=l.get_data('v(pp[13])')
V25=l.get_data('v(pp[14])')
V26=l.get_data('v(pp[15])')
V27=l.get_data('v(pp[16])')
V28=l.get_data('v(pp[17])')
V29=l.get_data('v(pp[18])')
V30=l.get_data('v(pp[19])')
V31=l.get_data('v(pp[20])')
V32=l.get_data('v(pp[21])')
V33=l.get_data('v(pp[22])')
V34=l.get_data('v(pp[23])')
V35=l.get_data('v(pp[24])')
V36=l.get_data('v(pp[25])')
V37=l.get_data('v(pp[26])')
V38=l.get_data('v(pp[27])')
V39=l.get_data('v(pp[28])')
V40=l.get_data('v(pp[29])')
V41=l.get_data('v(pp[30])')
V42=l.get_data('v(pp[31])')
V43=l.get_data('v(done)')
V44=l.get_data('v(B[0])')
V45=l.get_data('v(B[1])')
V46=l.get_data('v(B[2])')
V47=l.get_data('v(B[3])')
V48=l.get_data('v(B[7])')

signals =   [V1, V2, V3, V4, V5, V11, V12, V13, V14, V15, V16, V17, V18, V43, V6, V7, V8, V9, V10, V44, V45, V46, V47, V48]
sig_names = ["clk", "rst", "init", "sh", "add", "pp0", "pp1", "pp2", "pp3", "pp4", "pp5", "pp6", "pp7", "done", "A0", "A1", "A2", "A3", "A7", "B0", "B1", "B2", "B3", "B7"]

# Create stacked subplots
fig, axes = plt.subplots(24, 1, figsize=(12, 20), sharex=True)

for i, (ax, sig) in enumerate(zip(axes, signals)):
    ax.plot(time, sig, color='red', linewidth=1)  # Color gradient
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

plt.plot(time, V11+20)
plt.plot(time, V12+24)
plt.plot(time, V13+28)
plt.plot(time, V14+30)
plt.plot(time, V15+34)
plt.plot(time, V16+38)
plt.plot(time, V17+42)
plt.plot(time, V18+46)
plt.plot(time, V43+50)

plt.plot(time, V6+54)
plt.plot(time, V7+58)
plt.plot(time, V8+62)
plt.plot(time, V9+66)
plt.plot(time, V10+70)

plt.plot(time, V44+74)
plt.plot(time, V45+78)
plt.plot(time, V46+82)
plt.plot(time, V47+86)
plt.plot(time, V48+90)

plt.legend()
plt.grid()
plt.show()


