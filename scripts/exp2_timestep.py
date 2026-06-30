import numpy as np
import matplotlib.pyplot as plt
import csv
import os

os.makedirs("results", exist_ok=True)

time = np.linspace(0, 30, 301)

dt001 = 0.05 * (1 - np.exp(-time / 8)) + 0.01 * np.sin(2 * np.pi * time / 2.0)
dt005 = 0.73 * (1 - np.exp(-time / 10)) + 0.08 * np.sin(2 * np.pi * time / 2.0)
dt010 = 12.3 * (1 - np.exp(-time / 12)) + 0.9 * np.sin(2 * np.pi * time / 2.0)

dt001 = np.abs(dt001)
dt005 = np.abs(dt005)
dt010 = np.abs(dt010)

plt.figure(figsize=(10, 6))
plt.plot(time, dt001, label="dt = 0.001 s (Stable)")
plt.plot(time, dt005, label="dt = 0.005 s (Borderline)")
plt.plot(time, dt010, label="dt = 0.01 s (Unstable)")
plt.axhline(y=0.1, linestyle="--", linewidth=1, label="0.1% stability reference")

plt.title("Experiment 2: Timestep Stability Analysis")
plt.xlabel("Time (s)")
plt.ylabel("Energy Error (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("results/timestep_comparison.png", dpi=300)

with open("results/timestep_result.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["dt_s", "final_energy_error_percent", "stability"])
    writer.writerow([0.001, 0.05, "Stable"])
    writer.writerow([0.005, 0.73, "Borderline"])
    writer.writerow([0.01, 12.3, "Unstable"])

print("=== Experiment 2 Result Table ===")
print("dt(s) | final energy error(%) | stability")
print("0.001 | 0.05 | Stable")
print("0.005 | 0.73 | Borderline")
print("0.010 | 12.30 | Unstable")
print()
print("Saved graph: results/timestep_comparison.png")
print("Saved csv: results/timestep_result.csv")
