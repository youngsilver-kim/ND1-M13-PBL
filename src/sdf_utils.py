#!/usr/bin/env python3
"""
sdf_utils.py — SDF 파라미터 자동 변경 유틸리티

M13 실험 자동화 핵심 도구.
M7의 RobotArm3DOF 클래스처럼, SDF 파일을 프로그래밍으로 제어합니다.

ND1 피지컬 AI 전문가 과정  |  M13 물리 시뮬레이션 기초
"""
from __future__ import annotations
import re
import os
import math
import numpy as np


# ══════════════════════════════════════════════════════
# M13 물리 상수
# ══════════════════════════════════════════════════════
GRAVITY   = 9.81
MASS_BOT  = 2.0
DT_DEFAULT = 0.001

MU_CONDITIONS    = [0.1, 0.5, 1.0]
DT_CONDITIONS    = [0.001, 0.005, 0.01]
SIGMA_CONDITIONS = [0.0, 0.02, 0.1]


# ══════════════════════════════════════════════════════
# SDF 편집기
# ══════════════════════════════════════════════════════
class SDFEditor:
    """SDF 파일 파라미터를 프로그래밍으로 변경하는 클래스."""

    def __init__(self, sdf_path: str):
        self.path = os.path.expanduser(sdf_path)
        with open(self.path, encoding='utf-8') as f:
            self._original = f.read()
        self._current = self._original

    def set_friction(self, mu: float) -> 'SDFEditor':
        if not (0.0 <= mu <= 5.0):
            raise ValueError(f'μ={mu} 범위 오류 (0~5)')
        self._current = re.sub(r'(<mu>)[0-9.]+(<\/mu>)', rf'\g<1>{mu}\g<2>', self._current)
        self._current = re.sub(r'(<mu2>)[0-9.]+(<\/mu2>)', rf'\g<1>{mu}\g<2>', self._current)
        return self

    def set_timestep(self, dt: float) -> 'SDFEditor':
        if not (1e-5 <= dt <= 1.0):
            raise ValueError(f'Δt={dt} 범위 오류')
        self._current = re.sub(
            r'(<max_step_size>)[0-9.]+(<\/max_step_size>)',
            rf'\g<1>{dt}\g<2>', self._current)
        return self

    def set_imu_noise(self, stddev: float) -> 'SDFEditor':
        if stddev < 0:
            raise ValueError(f'σ={stddev} 음수 불가')
        self._current = re.sub(r'(<stddev>)[0-9.]+(<\/stddev>)', rf'\g<1>{stddev}\g<2>', self._current)
        return self

    def save(self) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(self._current)
        print(f'[SDF] 저장: {self.path}')

    def restore(self) -> None:
        self._current = self._original
        self.save()

    def get_params(self) -> dict:
        params = {}
        m = re.search(r'<mu>([0-9.]+)</mu>', self._current)
        if m: params['mu'] = float(m.group(1))
        m = re.search(r'<max_step_size>([0-9.]+)</max_step_size>', self._current)
        if m: params['dt'] = float(m.group(1))
        m = re.search(r'<stddev>([0-9.]+)</stddev>', self._current)
        if m: params['stddev'] = float(m.group(1))
        return params


# ══════════════════════════════════════════════════════
# 물리 이론 계산
# ══════════════════════════════════════════════════════
class PhysicsCalc:

    @staticmethod
    def friction_distance(mu: float, v0: float = 2.0, m: float = MASS_BOT, t: float = 10.0) -> float:
        """마찰력 모델 정지 거리: x = v₀² / (2μg)"""
        a = -mu * GRAVITY
        t_stop = v0 / (mu * GRAVITY)
        d_stop = v0**2 / (2 * mu * GRAVITY)
        return d_stop if t_stop <= t else v0 * t + 0.5 * a * t**2

    @staticmethod
    def pendulum_period(L: float = 1.0) -> float:
        """단진자 이론 주기 T = 2π√(L/g)"""
        return 2 * math.pi * math.sqrt(L / GRAVITY)

    @staticmethod
    def euler_energy_error(dt: float, theta0: float = 0.5, t_max: float = 5.0) -> float:
        """순수 Forward Euler 에너지 오차 (Gazebo DART와 다른 값 — 직접 비교 금지)

        비교표 (L=1m, theta0=0.5rad, t_max=5s):
            Δt=0.001s → Euler ≈4.9%  / Gazebo DART ≈0.08%
            Δt=0.005s → Euler ≈27%   / Gazebo DART ≈1.23%
            Δt=0.01s  → Euler ≈61%   / Gazebo DART ≈12.3%
        """
        L, g = 1.0, GRAVITY
        theta, omega = theta0, 0.0
        E0 = 0.5 * (L * omega)**2 + g * L * (1 - math.cos(theta))
        for _ in range(int(t_max / dt)):
            alpha = -(g / L) * theta
            theta += omega * dt
            omega += alpha * dt
        E_final = 0.5 * (L * omega)**2 + g * L * (1 - math.cos(theta))
        return abs(E_final - E0) / E0 * 100


# ══════════════════════════════════════════════════════
# rosbag2 데이터 로더
# rosbags API 버전별 자동 감지:
#   구버전(<0.9.10): rosbags.serde.deserialize_cdr
#   신버전(>=0.9.10): rosbags.typesys.get_typestore
# Track A(Pure Python) 사용 시 rosbags 미설치여도 import 오류 없음
# ══════════════════════════════════════════════════════
_ROSBAGS_OK = False
_deserialize_fn = None

try:
    from rosbags.typesys import Stores, get_typestore as _get_typestore
    _typestore = _get_typestore(Stores.ROS2_HUMBLE)
    def _deserialize_fn(rawdata, msgtype):
        return _typestore.deserialize_cdr(rawdata, msgtype)
    _ROSBAGS_OK = True
except ImportError:
    try:
        from rosbags.serde import deserialize_cdr as _old_deser
        def _deserialize_fn(rawdata, msgtype):  # type: ignore[misc]
            return _old_deser(rawdata, msgtype)
        _ROSBAGS_OK = True
    except ImportError:
        pass  # Track A는 정상, Track B만 영향


def load_odom(bag_path: str, topic: str = '/odom') -> np.ndarray:
    """rosbag2에서 odom 위치 데이터 로드 → shape (N, 2)"""
    if not _ROSBAGS_OK:
        print('[경고] rosbags 미설치 — pip install rosbags --break-system-packages')
        return np.empty((0, 2))
    from rosbags.rosbag2 import Reader
    path = os.path.expanduser(bag_path)
    xs, ys = [], []
    try:
        with Reader(path) as reader:
            connections = [c for c in reader.connections if c.topic == topic]
            for conn, ts, rawdata in reader.messages(connections=connections):
                msg = _deserialize_fn(rawdata, conn.msgtype)
                xs.append(msg.pose.pose.position.x)
                ys.append(msg.pose.pose.position.y)
    except Exception as e:
        print(f'[경고] bag 로드 실패 ({bag_path}): {e}')
        return np.empty((0, 2))
    return np.column_stack([xs, ys]) if xs else np.empty((0, 2))


def load_imu_angular_z(bag_path: str, topic: str = '/imu/data') -> np.ndarray:
    """rosbag2에서 IMU angular_velocity.z 데이터 로드 → 1D 배열"""
    if not _ROSBAGS_OK:
        print('[경고] rosbags 미설치 — pip install rosbags --break-system-packages')
        return np.array([])
    from rosbags.rosbag2 import Reader
    path = os.path.expanduser(bag_path)
    values = []
    try:
        with Reader(path) as reader:
            connections = [c for c in reader.connections if c.topic == topic]
            for conn, ts, rawdata in reader.messages(connections=connections):
                msg = _deserialize_fn(rawdata, conn.msgtype)
                values.append(msg.angular_velocity.z)
    except Exception as e:
        print(f'[경고] bag 로드 실패 ({bag_path}): {e}')
        return np.array([])
    return np.array(values)


if __name__ == '__main__':
    print('=== M13 SDF 유틸리티 테스트 ===')
    calc = PhysicsCalc()
    print('\n[실험 1 이론값]')
    for mu in MU_CONDITIONS:
        d = calc.friction_distance(mu=mu, v0=2.0, t=10.0)
        print(f'  μ={mu}: F={mu*MASS_BOT*GRAVITY:.2f}N → 이동거리={d:.3f}m')
    print(f'\n단진자 이론 주기: T={calc.pendulum_period():.3f}s')
    print('\n[실험 2 — Forward Euler 오차 (Gazebo DART와 다른 값)]')
    gazebo_ref = {0.001: "≈0.08%", 0.005: "≈1.23%", 0.01: "≈12.3%"}
    for dt in DT_CONDITIONS:
        err = calc.euler_energy_error(dt=dt)
        print(f'  Δt={dt}s → Euler {err:.2f}%  (DART: {gazebo_ref[dt]})')
