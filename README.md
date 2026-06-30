# ND1-M13-PBL
## Physical Simulation Fundamentals with Gazebo (ROS 2 Humble)

김영은 (Kim Youngeun)

---

# 1. Project Overview | 프로젝트 개요

## English

This project contains the experimental results for the ND1 Physical AI M13 laboratory.

Three fundamental physics simulation experiments were performed using Gazebo Fortress and ROS 2 Humble.

The objective is to investigate how different simulation parameters influence simulation accuracy and the Sim-to-Real gap.

Experiments include:

- Experiment 1 : Friction coefficient comparison
- Experiment 2 : Timestep stability analysis
- Experiment 3 : IMU Gaussian noise analysis

---

## 한국어

ND1 Physical AI M13 물리 시뮬레이션 실습 프로젝트입니다.

Gazebo Fortress와 ROS 2 Humble 환경에서 물리 시뮬레이션을 수행하였으며,

다음 세 가지 실험을 통해 물리 파라미터가 시뮬레이션 결과에 미치는 영향을 분석하였습니다.

- 실험 1 : 마찰계수 비교
- 실험 2 : Time Step 안정성 분석
- 실험 3 : IMU Gaussian Noise 분석

---

# 2. Development Environment | 개발 환경

| Item | Version |
|------|---------|
| Ubuntu | 22.04 |
| ROS2 | Humble |
| Gazebo | Fortress |
| Python | 3.10 |
| NumPy | Latest |
| Matplotlib | Latest |

---

# 3. Directory Structure | 프로젝트 구조

```
ND1_M13_PBL
│
├── worlds/
│   ├── friction_test.sdf
│   ├── pendulum_test.sdf
│   └── imu_noise_test.sdf
│
├── scripts/
│   ├── exp1_friction.py
│   ├── exp2_timestep.py
│   └── exp3_noise.py
│
├── results/
│   ├── friction_comparison.png
│   ├── timestep_comparison.png
│   ├── noise_analysis.png
│   ├── friction_result.csv
│   ├── timestep_result.csv
│   └── noise_result.csv
│
├── README.md
└── run.sh
```

---

# 4. Experiment 1 : Friction Coefficient

## Objective

Compare object motion under different friction coefficients.

Parameters

- μ = 0.1
- μ = 0.5
- μ = 1.0

Result

- Low friction → longest moving distance
- Medium friction → reduced movement
- High friction → object almost stationary

Output

- friction_comparison.png
- friction_result.csv

---

# 5. Experiment 2 : Timestep Stability

## Objective

Analyze numerical stability according to simulation timestep.

Parameters

- Δt = 0.001 s
- Δt = 0.005 s
- Δt = 0.01 s

Result

Smaller timesteps produce more stable simulations.

Larger timesteps increase numerical error and reduce simulation accuracy.

Output

- timestep_comparison.png
- timestep_result.csv

---

# 6. Experiment 3 : IMU Noise Analysis

## Objective

Evaluate Gaussian sensor noise.

Parameters

σ =

- 0.0
- 0.02
- 0.1

Result

Increasing σ produces wider Gaussian distributions and larger measurement uncertainty.

Output

- noise_analysis.png
- noise_result.csv

---

# 7. Generated Figures

The following figures are automatically generated.

- friction_comparison.png
- timestep_comparison.png
- noise_analysis.png

---

# 8. Execution

Run each experiment independently.

Experiment 1

```bash
python3 scripts/exp1_friction.py
```

Experiment 2

```bash
python3 scripts/exp2_timestep.py
```

Experiment 3

```bash
python3 scripts/exp3_noise.py
```

---

# 9. References

- ROS 2 Humble Documentation
- Gazebo Fortress Documentation
- Open Robotics
