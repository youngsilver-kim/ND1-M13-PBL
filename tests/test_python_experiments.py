#!/usr/bin/env python3
"""test_python_experiments.py — python/ 트랙 단위 테스트
실행: cd ND1_M13_PBL && python3 -m pytest tests/ -v
"""
import sys, os, math, pytest
import numpy as np
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, 'python'))

try:
    from exp1_euler_rk4 import euler_integrate, rk4_integrate, pendulum_ode, G, L
    EXP1_OK = True
except Exception: EXP1_OK = False

try:
    from exp2_friction_slope import block_on_slope, SLOPE_DEG
    EXP2_OK = True
except Exception: EXP2_OK = False

try:
    from exp3_inertia_gap import pendulum_with_inertia, detect_period
    EXP3_OK = True
except Exception: EXP3_OK = False


@pytest.mark.skipif(not EXP1_OK, reason='exp1_euler_rk4 미구현')
class TestEulerRK4:
    def test_euler_returns_tuple(self):
        r = euler_integrate(pendulum_ode, np.array([0.1,0.0]), (0,1), 0.1)
        assert r is not None, 'None 반환 — TODO 1 완성 필요'
        t,y=r; assert t is not None and y is not None

    def test_euler_shape(self):
        r = euler_integrate(pendulum_ode, np.array([0.1,0.0]), (0,1), 0.1)
        if r is None: pytest.skip('미구현')
        t,y=r; assert len(t)>0 and y.shape[1]==2

    def test_rk4_returns_tuple(self):
        r = rk4_integrate(pendulum_ode, np.array([0.1,0.0]), (0,1), 0.1)
        assert r is not None; t,y=r; assert t is not None and y is not None

    def test_rk4_more_accurate(self):
        y0=np.array([np.pi/4,0.0]); h=0.1
        ref=rk4_integrate(pendulum_ode, y0.copy(), (0,5), 0.0001)
        if ref is None: pytest.skip('미구현')
        t_ref,y_ref=ref
        res_e=euler_integrate(pendulum_ode, y0.copy(), (0,5), h)
        res_r=rk4_integrate(pendulum_ode,  y0.copy(), (0,5), h)
        if res_e is None or res_r is None: pytest.skip('미구현')
        t_e,y_e=res_e; t_r,y_r=res_r
        mae_e=float(np.mean(np.abs(y_e[:,0]-np.interp(t_e,t_ref,y_ref[:,0]))))
        mae_r=float(np.mean(np.abs(y_r[:,0]-np.interp(t_r,t_ref,y_ref[:,0]))))
        assert mae_r < mae_e, f'RK4({mae_r:.4e}) >= Euler({mae_e:.4e})'

    def test_rk4_energy_conservation(self):
        y0=np.array([np.pi/4,0.0])
        r=rk4_integrate(pendulum_ode, y0.copy(), (0,5), 0.001)
        if r is None: pytest.skip('미구현')
        t,y=r
        E0=0.5*(L*y[0,1])**2+G*L*(1-np.cos(y[0,0]))
        Ef=0.5*(L*y[-1,1])**2+G*L*(1-np.cos(y[-1,0]))
        if E0<1e-10: pytest.skip('초기 에너지 0')
        assert abs(Ef-E0)/E0*100 < 5.0


@pytest.mark.skipif(not EXP2_OK, reason='exp2_friction_slope 미구현')
class TestFrictionSlope:
    def test_returns_array(self):
        r=block_on_slope(np.array([0.0,1.0]), 0.0, mu=0.3)
        assert r is not None and len(r)==2

    def test_high_friction_stops(self):
        dy=block_on_slope(np.array([0.0,0.0]), 0.0, mu=1.0)
        if dy is None: pytest.skip('미구현')
        assert dy[1] <= 0.01, f'μ=1.0에서 블록 미끄러짐: a={dy[1]:.3f}'

    def test_low_friction_moves(self):
        dy=block_on_slope(np.array([0.0,0.01]), 0.0, mu=0.1)
        if dy is None: pytest.skip('미구현')
        assert dy[1] > 0, f'μ=0.1에서 블록 정지: a={dy[1]:.3f}'


@pytest.mark.skipif(not EXP3_OK, reason='exp3_inertia_gap 미구현')
class TestInertiaGap:
    def test_returns_array(self):
        r=pendulum_with_inertia(np.array([0.5,0.0]), 0.0, I_ratio=1.0)
        assert r is not None and len(r)==2

    def test_I_ratio_1_standard(self):
        state=np.array([0.5,0.2])
        std=np.array([state[1], -(9.81/1.0)*np.sin(state[0])])
        dy=pendulum_with_inertia(state, 0.0, I_ratio=1.0)
        if dy is None: pytest.skip('미구현')
        assert abs(dy[1]-std[1])<1e-9

    def test_large_I_slower(self):
        state=np.array([0.5,0.0])
        dy1=pendulum_with_inertia(state, 0.0, I_ratio=1.0)
        dy2=pendulum_with_inertia(state, 0.0, I_ratio=2.0)
        if dy1 is None or dy2 is None: pytest.skip('미구현')
        assert abs(dy2[1]) < abs(dy1[1])

    def test_small_I_faster(self):
        state=np.array([0.5,0.0])
        dy1 =pendulum_with_inertia(state, 0.0, I_ratio=1.0)
        dy05=pendulum_with_inertia(state, 0.0, I_ratio=0.5)
        if dy1 is None or dy05 is None: pytest.skip('미구현')
        assert abs(dy05[1]) > abs(dy1[1])
