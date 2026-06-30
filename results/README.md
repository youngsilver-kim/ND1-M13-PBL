# results/ 폴더

실험 결과 그래프와 bag 분석 결과가 저장됩니다.

## Track A 결과 (평가 제출용)
| 파일 | 생성 스크립트 |
|------|-------------|
| M13_exp1_euler_vs_rk4.png | python/exp1_euler_rk4.py |
| M13_exp2_friction.png | python/exp2_friction_slope.py |
| M13_exp3_inertia_gap.png | python/exp3_inertia_gap.py |

## Track B 결과 (Gazebo 실습)
| 파일 | 생성 스크립트 |
|------|-------------|
| friction_comparison.png | scripts/exp1_friction.py |
| timestep_comparison.png | scripts/exp2_timestep.py |
| noise_analysis.png | scripts/exp3_noise.py |
| m13_summary.png | scripts/visualize.py |

## Track B bag 저장 경로
```
results/
├── friction_mu0.1/  friction_mu0.5/  friction_mu1.0/   (실험 1)
├── pendulum_dt0.001/  dt0.005/  dt0.01/                (실험 2)
└── imu_sigma0.0/  sigma0.02/  sigma0.1/                (실험 3)
```

## ⚠️ 실험 1 주의
ign gazebo worlds/friction_test.sdf 직접 실행 시 오류 발생.
반드시 ros2 launch로 실행 → RUNBOOK.md 참조.
