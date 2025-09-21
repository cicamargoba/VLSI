#!/usr/bin/env python3
import ltspice
import matplotlib.pyplot as plt

# --- Load .raw ---
filepath = "Mult_4.raw"
l = ltspice.Ltspice(filepath)
l.parse()

time = l.get_time()
all_vars = l.getVariableNames()   # ✅ correct API

print("✅ Variables found in RAW file:")
print(all_vars)

# Exclude time
signals_to_plot = [v for v in all_vars if v.lower() != "time"]

signal_data = []
for var in signals_to_plot:
    try:
        sig = l.get_data(var)
        signal_data.append((var, sig))
    except Exception:
        print(f"⚠️ Could not read {var}, skipping.")

# --- Plot stacked compact ---
n = len(signal_data)
fig, axes = plt.subplots(n, 1, figsize=(12, 1.2*n), sharex=True)  # ~1.2 inch per signal

if n == 1:
    axes = [axes]

for i, (ax, (name, sig)) in enumerate(zip(axes, signal_data)):
    ax.plot(time, sig, color=plt.cm.viridis(i/max(1,n-1)), linewidth=0.8)
    ax.set_ylabel(name, rotation=0, ha='right', va='center', fontsize=7)
    ax.grid(alpha=0.2, linewidth=0.5)
    ax.tick_params(labelsize=7)

axes[-1].set_xlabel('Time (s)', fontsize=9)
plt.suptitle('Xyce Signals (Compact Stacked View)', y=0.94, fontsize=10)
plt.tight_layout(pad=0.2)
plt.show()
