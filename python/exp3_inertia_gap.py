#!/usr/bin/env python3
"""
exp3_inertia_gap.py — 평가 실험 3: 관성모멘트 오차 & Sim-to-Real 갭 [스켈레톤]

목표: 단진자 관성모멘트(I)를 잘못 추정했을 때 발생하는 운동 차이를 분석하고
      Sim-to-Real 갭의 원인을 실험적으로 재현

합격 기준:
    □  pendulum_with_inertia() 직접 구현
    □  I_ratio > 1.0 에서 진동 느려짐 확인
    □  I_ratio < 1.0 에서 진동 빨라짐 확인
    □  M13_exp3_inertia_gap.png 저장

실행:
    cd ND1_M13_PBL
    python3 python/exp3_inertia_gap.py

ND1 M13 | 물리 시뮬레이션 기초 | Track A 평가용
"""
import os, sys
import numpy as np
import matplotlib
import platform as _plat, matplotlib.font_manager as _fm
def _ko_font():
    s=_plat.system()
    if s=='Windows': matplotlib.rcParams['font.sans-serif']=['Malgun Gothic','DejaVu Sans']
    elif s=='Darwin': matplotlib.rcParams['font.sans-serif']=['AppleGothic','DejaVu Sans']
    else:
        avail={f.name for f in _fm.fontManager.ttflist}
        matplotlib.rcParams['font.sans-serif']=['NanumGothic','DejaVu Sans'] if 'NanumGothic' in avail else ['DejaVu Sans']
    matplotlib.rcParams['font.family']='sans-serif'
    matplotlib.rcParams['axes.unicode_minus']=False
    matplotlib.rcParams['mathtext.fontset']='dejavusans'
    import logging; logging.getLogger('matplotlib.mathtext').setLevel(logging.ERROR)
_ko_font()
import matplotlib.pyplot as plt

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
sys.path.insert(0, os.path.join(ROOT_DIR, 'python'))

try:
    from exp1_euler_rk4 import rk4_integrate
except ImportError:
    rk4_integrate = None

G=9.81; L=1.0; M=1.0; THETA0=np.pi/3; T_SPAN=(0.0,8.0); H=0.01
I_RATIOS=[0.5, 0.75, 1.0, 1.5, 2.0]


def pendulum_with_inertia(state: np.ndarray, t: float,
                           I_ratio: float=1.0,
                           g: float=G, L: float=L, m: float=M) -> np.ndarray:
    """관성모멘트 오차가 있는 단진자.
    α = -(g/L)*sin(θ) / I_ratio
    """
    # ──────────────────────────────────────────────────────
    # TODO 1: θ, ω = state / α = -(g/L)*sin(θ)/I_ratio
    #         return np.array([ω, α])
    # ──────────────────────────────────────────────────────
    pass  # ← 여기를 완성하세요


def detect_period(t_arr: np.ndarray, theta_arr: np.ndarray) -> float:
    crossings = []
    for i in range(len(theta_arr)-1):
        if theta_arr[i]*theta_arr[i+1] < 0:
            t_c = t_arr[i] + (-theta_arr[i])/(theta_arr[i+1]-theta_arr[i])*(t_arr[i+1]-t_arr[i])
            crossings.append(t_c)
    if len(crossings) < 2: return float('nan')
    return float(np.mean(np.diff(crossings))*2)


def run_simulation(I_ratio: float) -> tuple:
    if rk4_integrate is None: return None, None
    result = rk4_integrate(
        lambda s,t: pendulum_with_inertia(s,t,I_ratio=I_ratio),
        np.array([THETA0, 0.0]), T_SPAN, H
    )
    return result if result is not None else (None, None)


def plot_results(all_results: dict) -> None:
    fig,ax=plt.subplots(figsize=(12,5))
    colors=plt.cm.RdYlBu_r(np.linspace(0.1,0.9,len(I_RATIOS)))
    T_theory=2*np.pi*np.sqrt(L/G)
    for (I_ratio,(t,y)),color in zip(all_results.items(),colors):
        if t is None: continue
        lw=3.0 if I_ratio==1.0 else 1.5
        label=f'I_ratio={I_ratio}'+(' ← 기준' if I_ratio==1.0 else '')
        ax.plot(t,np.degrees(y[:,0]),color=color,linewidth=lw,label=label)
    ax.axhline(0,color='black',linestyle='--',linewidth=0.8,alpha=0.5)
    ax.set_xlabel('시간 (s)'); ax.set_ylabel('각도 (°)')
    ax.set_title(f'Sim-to-Real 갭 재현 — 관성모멘트 오차별 단진자 운동\n'
                 f'이론 주기: T={T_theory:.3f}s  |  θ₀={np.degrees(THETA0):.0f}°',fontweight='bold')
    ax.legend(fontsize=9); ax.grid(True,alpha=0.3)
    plt.tight_layout()
    os.makedirs(RESULTS_DIR,exist_ok=True)
    out=os.path.join(RESULTS_DIR,'M13_exp3_inertia_gap.png')
    plt.savefig(out,dpi=150,bbox_inches='tight')
    print(f'그래프 저장: {out}')


def main():
    print('=== M13 평가 실험 3: 관성모멘트 오차 & Sim-to-Real 갭 ===\n')
    T_theory=2*np.pi*np.sqrt(L/G)
    print(f'이론 주기 (I_ratio=1.0): T = {T_theory:.4f}s\n')
    all_results={}
    print(f'{"I_ratio":>8} | {"측정 주기(s)":>12} | {"기준 대비":>10} | {"해석"}')
    print('-'*55)
    ref_T=None
    for I_ratio in I_RATIOS:
        t,y=run_simulation(I_ratio); all_results[I_ratio]=(t,y)
        if t is None or y is None:
            print(f'{I_ratio:>8} | {"미구현":>12}'); continue
        T_meas=detect_period(t,y[:,0])
        if I_ratio==1.0: ref_T=T_meas
        if ref_T and not np.isnan(T_meas):
            diff_pct=(T_meas-ref_T)/ref_T*100
            note=f'{abs(diff_pct):.1f}% {"느림" if diff_pct>0 else "빠름"}'
        else: note='—'
        print(f'{I_ratio:>8} | {T_meas:>12.4f} | {note:>10}')
    print(f'\nSim-to-Real 해석:\n  I_ratio > 1.0 → 관성 과대 추정 → 진동 느림\n  I_ratio < 1.0 → 관성 과소 추정 → 진동 빠름')
    if any(v[0] is not None for v in all_results.values()):
        plot_results(all_results)
    print('\n✅ 실험 3 완료\n   다음: python3 python/visualize_python.py')

if __name__ == '__main__':
    main()
