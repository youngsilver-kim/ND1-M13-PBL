#!/usr/bin/env python3
"""
visualize_python.py — Pure Python 실험 1~3 종합 시각화 (완성본)
TODO 미완성 시 데모 모드로 실행됩니다.
실행: cd ND1_M13_PBL && python3 python/visualize_python.py
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
import matplotlib.gridspec as gridspec

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
sys.path.insert(0, os.path.join(ROOT_DIR, 'python'))

try:
    from exp1_euler_rk4      import euler_integrate, rk4_integrate, pendulum_ode, G as G1, L as L1
    from exp2_friction_slope import block_on_slope, MU_VALUES, T_SPAN, H, G as G2, SLOPE_DEG
    from exp3_inertia_gap    import pendulum_with_inertia, I_RATIOS, G as G3, L as L3, THETA0
    IMPORTS_OK = True
except Exception as e:
    IMPORTS_OK = False
    print(f'[경고] 임포트 실패 — TODO 미완성: {e}')
    print('       각 실험 TODO 완성 후 재실행하세요\n')


def demo_with_fallback():
    fig = plt.figure(figsize=(16, 10))
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # 패널 1: Euler vs RK4 오차
    ax1 = fig.add_subplot(gs[0, :2])
    if IMPORTS_OK:
        y0=np.array([np.pi/4, 0.0])
        t_ref,y_ref=rk4_integrate(pendulum_ode, y0.copy(), (0,10), 0.0001)
        for h,color,ls in [(0.1,'#D85A30','-'),(0.01,'#2E75B6','--'),(0.001,'#1D7A3A',':')]:
            t_e,y_e=euler_integrate(pendulum_ode, y0.copy(), (0,10), h)
            t_r,y_r=rk4_integrate(pendulum_ode, y0.copy(), (0,10), h)
            if t_e is None: continue
            ref_e=np.interp(t_e,t_ref,y_ref[:,0]); ref_r=np.interp(t_r,t_ref,y_ref[:,0])
            ax1.semilogy(t_e,np.maximum(np.abs(y_e[:,0]-ref_e),1e-15),color=color,ls=ls,lw=1.5,label=f'Euler h={h}')
            ax1.semilogy(t_r,np.maximum(np.abs(y_r[:,0]-ref_r),1e-15),color=color,ls='-.',lw=1,alpha=0.7,label=f'RK4 h={h}')
    else:
        t=np.linspace(0,10,100)
        ax1.semilogy(t,0.1*np.exp(0.3*t),'#D85A30',ls='-',label='Euler h=0.1 (데모)')
        ax1.semilogy(t,1e-4*np.ones_like(t),'#2E75B6',ls='--',label='RK4 h=0.01 (데모)')
    ax1.set_title('실험 1: Euler vs RK4 수치적분 오차 (log scale)',fontweight='bold')
    ax1.set_xlabel('시간 (s)'); ax1.set_ylabel('|오차| (rad)')
    ax1.legend(fontsize=8); ax1.grid(True,alpha=0.3,which='both')

    # 패널 2: 마찰계수별 이동거리
    ax2 = fig.add_subplot(gs[0, 2])
    mu_crit=np.tan(np.radians(SLOPE_DEG)) if IMPORTS_OK else 0.577
    if IMPORTS_OK:
        colors=plt.cm.viridis(np.linspace(0,1,len(MU_VALUES)))
        for mu,color in zip(MU_VALUES,colors):
            t=np.arange(*T_SPAN,H); y=np.zeros((len(t),2))
            for i in range(len(t)-1):
                dy=block_on_slope(y[i],t[i],mu=mu)
                if dy is None: break
                y[i+1]=y[i]+H*dy
            ax2.plot(t,y[:,0],color=color,linewidth=2,label=f'μ={mu}')
    else:
        for mu,color in zip([0.1,0.3,0.5,0.8,1.0],['#2166AC','#4DAC26','#F1A340','#D6604D','#762A83']):
            t=np.linspace(0,3,100)
            d=np.maximum(0,0.5*(9.81*np.sin(np.radians(30))-mu*9.81*np.cos(np.radians(30)))*t**2)
            ax2.plot(t,d,linewidth=2,label=f'μ={mu} (demo)')
    ax2.set_title(f'실험 2: 마찰 경사면\n(μ_crit≈{mu_crit:.3f})',fontweight='bold')
    ax2.set_xlabel('시간 (s)'); ax2.set_ylabel('이동 거리 (m)')
    ax2.legend(fontsize=7); ax2.grid(True,alpha=0.3)

    # 패널 3: 관성모멘트 오차별 단진자
    ax3 = fig.add_subplot(gs[1, :])
    T_theory=2*np.pi*np.sqrt(L3/G3) if IMPORTS_OK else 2.006
    ratios=I_RATIOS if IMPORTS_OK else [0.5,0.75,1.0,1.5,2.0]
    colors_i=plt.cm.RdYlBu_r(np.linspace(0.1,0.9,len(ratios)))
    if IMPORTS_OK:
        y0=np.array([THETA0,0.0])
        for I_ratio,color in zip(ratios,colors_i):
            t,y=rk4_integrate(lambda s,t: pendulum_with_inertia(s,t,I_ratio=I_ratio),y0.copy(),(0,8),0.01)
            if t is None: continue
            lw=2.5 if I_ratio==1.0 else 1.2
            ax3.plot(t,np.degrees(y[:,0]),color=color,linewidth=lw,
                     label=f'I_ratio={I_ratio}'+(' ← 기준' if I_ratio==1.0 else ''))
    else:
        for I_ratio,color in zip(ratios,colors_i):
            t=np.linspace(0,8,300); T_i=2*np.pi*np.sqrt(1.0/9.81)*np.sqrt(I_ratio)
            theta=(np.pi/3)*np.cos(2*np.pi/T_i*t)
            ax3.plot(t,np.degrees(theta),color=color,linewidth=2.5 if I_ratio==1.0 else 1.2,
                     label=f'I_ratio={I_ratio} (demo)')
    ax3.axhline(0,color='black',linestyle='--',linewidth=0.8,alpha=0.5)
    ax3.set_title(f'실험 3: Sim-to-Real 갭 (관성모멘트 오차)\n이론 주기: T={T_theory:.3f}s',fontweight='bold')
    ax3.set_xlabel('시간 (s)'); ax3.set_ylabel('각도 (°)')
    ax3.legend(fontsize=9,ncol=5); ax3.grid(True,alpha=0.3)

    status='(실제 구현)' if IMPORTS_OK else '(데모 — TODO 완성 후 재실행)'
    fig.suptitle(f'M13 Pure Python 실험 1~3 종합 결과 {status}',fontsize=14,fontweight='bold')
    plt.tight_layout()
    os.makedirs(RESULTS_DIR,exist_ok=True)
    out=os.path.join(RESULTS_DIR,'M13_python_summary.png')
    plt.savefig(out,dpi=150,bbox_inches='tight')
    print(f'저장: {out}')


def main():
    print('=== M13 Pure Python 실험 종합 시각화 ===\n')
    if not IMPORTS_OK:
        print('[데모 모드] TODO 미완성 상태입니다. 데모 그래프를 생성합니다.\n')
    demo_with_fallback()
    print('\n완료.')

if __name__ == '__main__':
    main()
