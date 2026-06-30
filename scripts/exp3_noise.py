import numpy as np
import matplotlib.pyplot as plt
import csv
import os

os.makedirs("results", exist_ok=True)

np.random.seed(42)

sigmas=[0.0,0.02,0.1]

labels=[
    "σ = 0.0",
    "σ = 0.02",
    "σ = 0.1"
]

plt.figure(figsize=(10,6))

summary=[]

for sigma,label in zip(sigmas,labels):

    if sigma==0:
        data=np.zeros(5000)
    else:
        data=np.random.normal(0,sigma,5000)

    plt.hist(
        data,
        bins=60,
        density=True,
        alpha=0.45,
        label=label
    )

    summary.append([sigma,np.std(data)])

plt.title("Experiment 3: IMU Gaussian Noise Distribution")
plt.xlabel("Sensor Noise")
plt.ylabel("Probability Density")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("results/noise_analysis.png",dpi=300)

with open("results/noise_result.csv","w",newline="") as f:

    writer=csv.writer(f)

    writer.writerow(["sigma","measured_std"])

    writer.writerows(summary)

print("=== Experiment 3 ===")

for row in summary:

    print(f"sigma={row[0]:.2f}   measured std={row[1]:.4f}")

print()

print("Saved graph : results/noise_analysis.png")
print("Saved csv   : results/noise_result.csv")