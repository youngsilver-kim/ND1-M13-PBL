# python/ — Pure Python 평가 트랙

> M13 평가문항 기준 | Gazebo·ROS2 불필요 | numpy·scipy·matplotlib만 사용

## 실행 순서

```bash
cd ND1_M13_PBL   # 반드시 루트에서

python3 python/exp1_euler_rk4.py        # 실험 1: Euler vs RK4 (TODO 2개)
python3 python/exp2_friction_slope.py   # 실험 2: 경사면 마찰 (TODO 1개)
python3 python/exp3_inertia_gap.py      # 실험 3: Sim-to-Real 갭 (TODO 1개)
python3 python/visualize_python.py      # 종합 (데모 모드 지원)

# 또는 한 번에:
bash run.sh python
```

## TODO 목록

| 파일 | 함수 | 내용 |
|------|------|------|
| exp1_euler_rk4.py | euler_integrate() | y[i+1] = y[i] + h·f(y[i], t[i]) |
| exp1_euler_rk4.py | rk4_integrate() | k1~k4 가중 평균 |
| exp2_friction_slope.py | block_on_slope() | F_grav = g·sin(θ), F_fric = μg·cos(θ) |
| exp3_inertia_gap.py | pendulum_with_inertia() | α = -(g/L)·sin(θ) / I_ratio |

## 평가 기준 (Track A)

| 항목 | 배점 |
|------|------|
| 실험 1: euler/rk4 구현 + MAE 표 + 그래프 | 15점 |
| 실험 2: block_on_slope 구현 + 이동거리 표 + 그래프 | 15점 |
| 실험 3: pendulum_with_inertia + 주기 비교 + Sim2Real 해석 | 15점 |
| 코드 품질 (주석·구조·재현성) | 5점 |
