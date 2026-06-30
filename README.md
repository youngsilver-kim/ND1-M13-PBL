# M13 — 물리 시뮬레이션 기초  |  [이름] / [날짜]

## 1. 프로젝트 개요

ND1 피지컬 AI 전문가 과정 M13 실험 결과물입니다.
마찰계수(μ), 타임스텝(Δt), 센서 노이즈(σ) 3가지 파라미터가
Sim-to-Real 갭에 미치는 영향을 수치 실험과 Gazebo 시뮬레이터로 측정합니다.

---

## ⚡ 2가지 실행 트랙

### Track A — Pure Python (평가 제출용, Gazebo 불필요)

```bash
cd ND1_M13_PBL
bash run.sh python
# 또는 개별:
python3 python/exp1_euler_rk4.py
python3 python/exp2_friction_slope.py
python3 python/exp3_inertia_gap.py
```

| 파일 | 함수 | 합격 기준 |
|------|------|----------|
| python/exp1_euler_rk4.py | euler_integrate() / rk4_integrate() | MAE 표 + PNG |
| python/exp2_friction_slope.py | block_on_slope() | μ=1.0에서 블록 정지 |
| python/exp3_inertia_gap.py | pendulum_with_inertia() | I_ratio별 주기 차이 |

### Track B — Gazebo 시뮬레이션 (심화용, ROS2+Gazebo 필요)

> ⚠️ **실험 1은 `ign gazebo` 직접 실행 불가 — ros2 launch 사용 (RUNBOOK.md 참조)**

```bash
bash run.sh verify   # 환경 검증
bash run.sh all      # 전체 분석
```

---

## 2. 실행 환경

| 항목 | Track A | Track B |
|------|---------|---------|
| Python 3.10+ numpy scipy matplotlib | ✅ 필수 | ✅ 필수 |
| Ubuntu 22.04 / ROS2 Humble / Gazebo Fortress | 불필요 | ✅ 필수 |
| rosbags | 불필요 | ✅ 필수 |

```bash
# 공통 설치
pip3 install -r requirements.txt --break-system-packages

# Track B 추가 (ROS2 환경)
sudo apt install -y ros-humble-ros-gz-sim ros-humble-ros-gz-bridge
sudo apt install -y ros-humble-turtlebot4-simulator
```

---

## 3. 디렉터리 구조

```
ND1_M13_PBL/
├── python/      ← Track A: 평가 실험 (TODO 완성 필요)
├── scripts/     ← Track B: Gazebo bag 분석 (TODO 완성 필요)
├── src/         ← 공통 유틸리티 (sdf_utils.py — 수정 불필요)
├── worlds/      ← Gazebo SDF 파일 (파라미터 변경 위치)
├── results/     ← 실험 결과 저장 위치
├── tests/       ← 단위 테스트 (pytest)
├── run.sh       ← 실행 스크립트
├── RUNBOOK.md   ← 1분 재현 가이드
└── requirements.txt
```

---

## 4. 오류 해결

| 오류 | 해결 |
|------|------|
| ModuleNotFoundError: sdf_utils | `cd ND1_M13_PBL` 후 실행 |
| None 반환 (exp1~3) | pass → 함수 구현 |
| Gazebo 검은 화면 | `export LIBGL_ALWAYS_SOFTWARE=1` |
| Unable to find uri[model://turtlebot4] | ros2 launch 사용 (RUNBOOK.md) |
| bag record 즉시 Stopped | Gazebo + 로봇 먼저 실행 후 녹화 |
