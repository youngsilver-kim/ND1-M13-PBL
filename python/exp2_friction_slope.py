#!/usr/bin/env python3
"""
exp2_friction_slope.py — 평가 실험 2: 마찰계수별 경사면 블록 미끄러짐 [스켈레톤]

목표: 경사면(θ=30°) 위 블록의 미끄러짐을 뉴턴 방정식으로 모델링하고
      마찰계수(μ) 변화에 따른 이동 거리·속도 변화를 분석

합격 기준:
    □  block_on_slope() 직접 구현
    □  μ=1.0에서 블록 정지 확인 (tan30°≈0.577)
    □  M13_exp2_friction.png 저장

실행:
    cd ND1_M13_PBL
    python3 python/exp2_friction_slope.py

ND1 M13 | 물리 시뮬레이션 기초 | Track A 평가용
"""
import os, sys
import numpy as np
import matplotlib
import platform as _plat, matplotlib.font_manager as _fm
def _ko_font():
    s = _plat.system()
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

G=9.81; SLOPE_DEG=30.0; MU_VALUES=[0.1,0.3,0.5,0.8,1.0]; T_SPAN=(0.0,3.0); H=0.01


def block_on_slope(state: np.ndarray, t: float,
                   mu: float, g: float=G, slope_deg: float=SLOPE_DEG) -> np.ndarray:
    """경사면 위 블록 운동 방정식."""
    # ──────────────────────────────────────────────────────
    # TODO 1: θ = np.radians(slope_deg) / v = state[1]
    #   F_grav = g*sin(θ) / F_fric = mu*g*cos(θ)*sign(v)
    #   a = F_grav - F_fric
    #   주의: v=0이면 정적 평형 조건 (sin(θ) <= mu*cos(θ)) 확인
    # ──────────────────────────────────────────────────────
    pass  # ← 여기를 완성하세요


def run_simulation(mu: float) -> tuple:
    if rk4_integrate is None:
        y0=np.array([0.0,0.0]); t_arr=np.arange(*T_SPAN,H)
        y_arr=np.zeros((len(t_arr),2)); y_arr[0]=y0
        for i in range(len(t_arr)-1):
            dy=block_on_slope(y_arr[i],t_arr[i],mu=mu)
            if dy is None: return None, None
            y_arr[i+1]=y_arr[i]+H*dy
        return t_arr, y_arr
    result=rk4_integrate(lambda s,t: block_on_slope(s,t,mu=mu), np.array([0.0,0.0]), T_SPAN, H)
    return result if result is not None else (None, None)


def plot_results(all_results: dict) -> None:
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,5))
    colors=plt.cm.viridis(np.linspace(0,1,len(MU_VALUES)))
    for (mu,(t,y)),color in zip(all_results.items(),colors):
        if t is None: continue
        ax1.plot(t,y[:,0],color=color,linewidth=2,label=f'μ={mu}')
        ax2.plot(t,y[:,1],color=color,linewidth=2,label=f'μ={mu}')
    mu_crit=np.tan(np.radians(SLOPE_DEG))
    ax1.set_title(f'이동 거리 vs 시간  (μ_crit=tan30°≈{mu_crit:.3f})',fontweight='bold')
    ax1.set_xlabel('시간 (s)'); ax1.set_ylabel('이동 거리 (m)')
    ax1.legend(fontsize=9); ax1.grid(True,alpha=0.3)
    ax2.set_title('속도 vs 시간',fontweight='bold')
    ax2.set_xlabel('시간 (s)'); ax2.set_ylabel('속도 (m/s)')
    ax2.axhline(0,color='black',linestyle='--',alpha=0.5)
    ax2.legend(fontsize=9); ax2.grid(True,alpha=0.3)
    plt.suptitle('경사면(30°) 블록 미끄러짐 — 마찰계수별 비교',fontsize=13,fontweight='bold')
    plt.tight_layout()
    os.makedirs(RESULTS_DIR,exist_ok=True)
    out=os.path.join(RESULTS_DIR,'M13_exp2_friction.png')
    plt.savefig(out,dpi=150,bbox_inches='tight')
    print(f'그래프 저장: {out}')


def main():
    print('=== M13 평가 실험 2: 마찰계수별 경사면 미끄러짐 ===\n')
    mu_crit=np.tan(np.radians(SLOPE_DEG))
    print(f'경사각: {SLOPE_DEG}° | 정지 임계 μ = tan({SLOPE_DEG}°) = {mu_crit:.3f}\n')
    all_results={}
    print(f'{"μ":>6} | {"3초 후 위치(m)":>14} | {"최종 속도(m/s)":>14} | {"정지 여부"}')
    print('-'*55)
    for mu in MU_VALUES:
        t,y=run_simulation(mu); all_results[mu]=(t,y)
        if t is None or y is None:
            print(f'{mu:>6} | {"미구현":>14} | {"미구현":>14}'); continue
        stopped='✅ 정지' if abs(y[-1,1])<0.01 else '▶ 이동 중'
        print(f'{mu:>6} | {y[-1,0]:>14.4f} | {y[-1,1]:>14.4f} | {stopped}')
    if any(v[0] is not None for v in all_results.values()):
        plot_results(all_results)
    print('\n✅ 실험 2 완료\n   다음: python3 python/exp3_inertia_gap.py')

if __name__ == '__main__':
    main()
