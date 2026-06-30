import numpy as np
import matplotlib.pyplot as plt
import csv
import os

os.makedirs("results", exist_ok=True)

# Experiment 1: Friction coefficient comparison
# Modified for the slope-based sliding box experiment

g = 9.81
theta_deg = 45
theta = np.deg2rad(theta_deg)

mus = [0.1, 0.5, 1.0]
labels = ["mu = 0.1 (Low friction)", "mu = 0.5 (Medium friction)", "mu = 1.0 (High friction)"]

time = np.linspace(0, 5, 501)

distance_logs = []
summary = []

for mu in mus:
    # Acceleration on inclined plane: a = g(sin(theta) - mu*cos(theta))
    a = g * (np.sin(theta) - mu * np.cos(theta))

    if a <= 0:
        distance = np.zeros_like(time)
        final_distance = 0.0
        interpretation = "Stopped or nearly stationary"
    else:
        distance = 0.5 * a * time ** 2

        # Limit by slope length for realistic visualization
        distance = np.minimum(distance, 4.0)
        final_distance = distance[-1]

        if mu == 0.1:
            interpretation = "Fast sliding due to low friction"
        elif mu == 0.5:
            interpretation = "Slow sliding due to medium friction"
        else:
            interpretation = "Nearly stopped due to high friction"

    distance_logs.append(distance)

    # Theoretical stopping distance for original PPT condition v0=2.0 m/s
    # x = v0^2 / (2*mu*g)
    v0 = 2.0
    theory_distance = v0 ** 2 / (2 * mu * g)

    summary.append([mu, final_distance, theory_distance, interpretation])

plt.figure(figsize=(10, 6))

for label, distance in zip(labels, distance_logs):
    plt.plot(time, distance, label=label)

plt.title("Experiment 1: Friction Coefficient Comparison")
plt.xlabel("Time (s)")
plt.ylabel("Moving Distance (m)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("results/friction_comparison.png", dpi=300)

with open("results/friction_result.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["mu", "slope_experiment_distance_m", "ppt_theory_distance_m", "interpretation"])
    writer.writerows(summary)

print("=== Experiment 1 Result Table ===")
print("mu | slope distance(m) | PPT theory distance(m) | interpretation")
for row in summary:
    print(f"{row[0]} | {row[1]:.3f} | {row[2]:.3f} | {row[3]}")

print()
print("Saved graph: results/friction_comparison.png")
print("Saved csv: results/friction_result.csv")