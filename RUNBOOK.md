# M13 — RUNBOOK (1분 재현 가이드)

## ⚡ 트랙 선택

| 트랙 | 명령 | 필요 환경 | 용도 |
|------|------|----------|------|
| Track A | `bash run.sh python` | Python만 | **평가 제출 (기본)** |
| Track B | `bash run.sh all` | ROS2+Gazebo | 심화·포트폴리오 |

---

## Track A — 한 줄 재현 (Gazebo 불필요)

```bash
cd ND1_M13_PBL && bash run.sh python
```

### 설치 (Track A)

```bash
# 권장: venv 사용
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 또는 전역 설치
pip3 install -r requirements.txt --break-system-packages
```

### Track A 핵심 수치 (구현 후 확인)

| 지표 | 기대값 |
|------|--------|
| Euler MAE (h=0.1) | ~14.0 (RK4보다 약 37,000배 큰 오차) |
| RK4 MAE (h=0.1) | ~3.7e-4 |
| 경사면 μ 임계값 | tan(30°)≈0.577 초과 시 블록 정지 |
| I_ratio=0.5 주기 | 기준 대비 ~29% 빠름 |
| I_ratio=2.0 주기 | 기준 대비 ~41% 느림 |

---

## Track B — Gazebo 환경 설정

> ⚠️ **Track B는 venv 사용 불가** — ROS2는 시스템 Python 사용

```bash
sudo apt install ros-humble-ros-gz-sim ros-humble-ros-gz-bridge
sudo apt install ros-humble-turtlebot4-simulator
pip3 install -r requirements.txt --break-system-packages
```

### IGN_GAZEBO_RESOURCE_PATH 설정 (필수)

```bash
source /opt/ros/humble/setup.bash
python3 - << 'PYEOF' >> ~/.bashrc
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
tb4   = get_package_share_directory('turtlebot4_ignition_bringup')
iro   = get_package_share_directory('irobot_create_ignition_bringup')
td    = get_package_share_directory('turtlebot4_description')
id_   = get_package_share_directory('irobot_create_description')
path  = ':'.join([os.path.join(tb4,'worlds'), os.path.join(iro,'worlds'),
    str(Path(td).parent.resolve()), str(Path(id_).parent.resolve())])
print(f'\nexport IGN_GAZEBO_RESOURCE_PATH={path}')
PYEOF
source ~/.bashrc
```

### 실험 1 — 마찰계수 (TurtleBot4 필요)

> ⚠️ `ign gazebo worlds/friction_test.sdf` 직접 실행 **불가** → ros2 launch 사용

```bash
# 터미널 1
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=friction_test

# 터미널 2 (로봇 안정화 30초 후)
ros2 bag record -o results/friction_mu0.5 /odom &
BAG_PID=$! && sleep 1
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}}"
sleep 0.3 && ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}}"
sleep 5 && kill $BAG_PID
python3 scripts/exp1_friction.py
```

### 실험 2·3 — 타임스텝·노이즈 (TurtleBot4 불필요)

```bash
# 실험 2 — ign gazebo 직접 실행 가능
ign gazebo worlds/pendulum_test.sdf
# 별도 터미널: ros2 bag record -o results/pendulum_dt0.001 /joint_states /imu/data

# 실험 3 — ign gazebo 직접 실행 가능
ign gazebo worlds/noise_test.sdf
# 별도 터미널: ros2 bag record -o results/imu_sigma0.02 /imu/data
```

---

## 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| ModuleNotFoundError: sdf_utils | 루트 아닌 위치 | `cd ND1_M13_PBL` 후 재실행 |
| ModuleNotFoundError: rclpy | venv 활성화 상태 | `deactivate` 후 재실행 |
| exp1: None 반환 | TODO 미구현 | pass → 함수 구현 |
| Gazebo 검은 화면 | GPU 미지원 | `export LIBGL_ALWAYS_SOFTWARE=1` |
| Unable to find uri[model://turtlebot4] | model.sdf 없음 | ros2 launch 사용 |
| bag record 즉시 Stopped | Gazebo 미실행 | Gazebo + 로봇 먼저 실행 후 녹화 |
| std가 σ와 다름 | 샘플 부족 | 30초 이상 녹화 (3000개+ 필요) |
| μ별 거리 차이 없음 | cmd_vel 지속 발행 | 순간 발사 방식 사용 |
