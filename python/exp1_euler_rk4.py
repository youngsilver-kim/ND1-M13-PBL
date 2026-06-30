#!/usr/bin/env python3
"""
exp1_euler_rk4.py — 평가 실험 1: Euler vs RK4 수치적분 비교  [스켈레톤]

합격 기준:
    □  euler_integrate() 직접 구현 (scipy 미사용)
    □  rk4_integrate() k1~k4 모두 계산
    □  3가지 h 값 MAE 정량 출력
    □  M13_exp1_euler_vs_rk4.png 저장 (log scale y축)

실행:
    cd ND1_M13_PBL
    python3 python/exp1_euler_rk4.py

ND1 M13 | 물리 시뮬레이션 기초 | Track A 평가용
"""
import os
import numpy as np
import matplotlib
import matplotlib.ticker as mticker

class _AsciiMinusLogFormatter(mticker.Formatter):
    def __call__(self, x, pos=None):
        if x <= 0: return ''
        exp = int(round(np.log10(x)))
        if abs(x - 10**exp) / (10**exp) > 1e-9:
            return f'{x:.1e}'.replace('e-0','e-').replace('e+0','e')
        sign = '-' if exp < 0 else ''
        return f'10^{sign}{abs(exp)}'

import platform as _plat, matplotlib.font_manager as _fm
def _ko_font():
    s = _plat.system()
    if s == 'Windows':
        matplotlib.rcParams['font.sans-serif'] = ['Malgun Gothic','DejaVu Sans']
    elif s == 'Darwin':
        matplotlib.rcParams['font.sans-serif'] = ['AppleGothic','DejaVu Sans']
    else:
        avail = {f.name for f in _fm.fontManager.ttflist}
        matplotlib.rcParams['font.sans-serif'] = (
            ['NanumGothic','DejaVu Sans'] if 'NanumGothic' in avail else ['DejaVu Sans'])
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['mathtext.fontset'] = 'dejavusans'
    import logging; logging.getLogger('matplotlib.mathtext').setLevel(logging.ERROR)
_ko_font()
import matplotlib.pyplot as plt

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
G = 9.81; L = 1.0

def pendulum_ode(state: np.ndarray, t: float) -> np.ndarray:
    theta, omega = state
    return np.array([omega, -(G / L) * np.sin(theta)])


def euler_integrate(f, y0: np.ndarray, t_span: tuple, h: float) -> tuple:
    """오일러 전진 적분. 점화식: y[i+1] = y[i] + h·f(y[i], t[i])"""
    # ──────────────────────────────────────────────────────
    # TODO 1: t_array = np.arange(t_span[0], t_span[1], h)
    #         y_array 초기화: shape=(len(t_array), len(y0))
    #         루프: y[i+1] = y[i] + h * f(y[i], t[i])
    # ──────────────────────────────────────────────────────
    pass  # ← 여기를 완성하세요


def rk4_integrate(f, y0: np.ndarray, t_span: tuple, h: float) -> tuple:
    """4차 룬게-쿠타. k1~k4 계산 후 가중 평균."""
    # ──────────────────────────────────────────────────────
    # TODO 2: k1=f(y,t), k2=f(y+h/2*k1,t+h/2), ...
    #         y[i+1] = y[i] + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
    # ──────────────────────────────────────────────────────
    pass  # ← 여기를 완성하세요


def compute_reference(t_span=(0,10), h_ref=0.0001) -> tuple:
    print(f'기준값 계산 중 (h={h_ref})...')
    result = rk4_integrate(pendulum_ode, np.array([np.pi/4, 0.0]), t_span, h_ref)
    return result if result is not None else (None, None)

def compute_mae(t_test, y_test, t_ref, y_ref) -> float:
    ref = np.interp(t_test, t_ref, y_ref[:, 0])
    return float(np.mean(np.abs(y_test[:, 0] - ref)))

def plot_results(results: dict, t_ref, y_ref) -> None:
    h_values = sorted(results.keys())
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, h in zip(axes, h_values):
        t_e, y_e = results[h]['euler']; t_r, y_r = results[h]['rk4']
        ref_e = np.interp(t_e, t_ref, y_ref[:, 0])
        ref_r = np.interp(t_r, t_ref, y_ref[:, 0])
        ax.semilogy(t_e, np.maximum(np.abs(y_e[:,0]-ref_e), 1e-15),
                    '#D85A30', lw=1.5, label='Euler')
        ax.semilogy(t_r, np.maximum(np.abs(y_r[:,0]-ref_r), 1e-15),
                    '#2E75B6', lw=1.5, label='RK4')
        ax.yaxis.set_major_formatter(_AsciiMinusLogFormatter())
        mae_e = float(np.mean(np.abs(y_e[:,0]-ref_e)))
        mae_r = float(np.mean(np.abs(y_r[:,0]-ref_r)))
        ax.set_title(f'h={h}s\nEuler MAE={mae_e:.2e}  |  RK4 MAE={mae_r:.2e}')
        ax.set_xlabel('시간 (s)'); ax.set_ylabel('|오차| (rad, log)')
        ax.legend(fontsize=9); ax.grid(True, alpha=0.3, which='both')
    plt.suptitle('단진자 수치적분 오차 비교 — Euler vs RK4', fontsize=13, fontweight='bold')
    plt.tight_layout()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = os.path.join(RESULTS_DIR, 'M13_exp1_euler_vs_rk4.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f'그래프 저장: {out}')

def main():
    print('=== M13 평가 실험 1: Euler vs RK4 수치적분 비교 ===\n')
    y0 = np.array([np.pi/4, 0.0]); t_span=(0.0,10.0); H_VALUES=[0.1,0.01,0.001]
    t_ref, y_ref = compute_reference(t_span)
    if t_ref is None:
        print('[주의] rk4_integrate() 미구현 — TODO 2를 먼저 완성하세요'); return
    results = {}
    print('\n[Step 1] 수치 적분 실행')
    for h in H_VALUES:
        t_e, y_e = euler_integrate(pendulum_ode, y0.copy(), t_span, h)
        t_r, y_r = rk4_integrate(pendulum_ode,  y0.copy(), t_span, h)
        results[h] = {'euler': (t_e, y_e), 'rk4': (t_r, y_r)}
    print('\n[Step 2] MAE 비교')
    print(f'{"h":>8} | {"Euler MAE":>12} | {"RK4 MAE":>12} | {"개선 배율":>10}')
    print('-'*50)
    for h in H_VALUES:
        t_e, y_e = results[h]['euler']; t_r, y_r = results[h]['rk4']
        if t_e is None or t_r is None:
            print(f'{h:>8} | {"미구현":>12} | {"미구현":>12}'); continue
        mae_e = compute_mae(t_e, y_e, t_ref, y_ref)
        mae_r = compute_mae(t_r, y_r, t_ref, y_ref)
        print(f'{h:>8} | {mae_e:>12.4e} | {mae_r:>12.4e} | {mae_e/max(mae_r,1e-20):>10.1f}x')
    if all(results[h]['euler'][0] is not None for h in H_VALUES):
        print('\n[Step 3] 그래프 생성')
        plot_results(results, t_ref, y_ref)
    print('\n✅ 실험 1 완료\n   다음: python3 python/exp2_friction_slope.py')

if __name__ == '__main__':
    main()
