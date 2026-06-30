#!/usr/bin/env python3
"""
visualize.py — M13 실험 결과 종합 시각화 (완성본)
bag 없이도 데모 모드로 실행 가능.
실행: cd ND1_M13_PBL && python3 scripts/visualize.py
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'src'))
from sdf_utils import (
    load_odom, load_imu_angular_z, PhysicsCalc,
    MU_CONDITIONS, DT_CONDITIONS, SIGMA_CONDITIONS, MASS_BOT, GRAVITY
)
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')


def _load_or_demo(bag_path, loader, demo_fn):
    return loader(bag_path) if os.path.exists(bag_path) else demo_fn()


def build_summary_figure() -> plt.Figure:
    calc = PhysicsCalc()
    fig  = plt.figure(figsize=(16, 12))
    gs   = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    # ── 패널 1: 실험 1 — 마찰계수별 이동 거리 ─────────────
    ax1 = fig.add_subplot(gs[0, 0])
    sim_vals, theory_vals = [], []
    for mu in MU_CONDITIONS:
        theory = calc.friction_distance(mu=mu, v0=2.0, t=10.0)
        bag    = os.path.join(RESULTS_DIR, f'friction_mu{mu}')
        traj   = _load_or_demo(bag, load_odom,
                    lambda mu_=mu: np.array([[i*0.3/max(1+mu_*GRAVITY/0.3,0.01),0] for i in range(100)]))
        sim    = float(np.linalg.norm(traj[-1]-traj[0])) if len(traj)>1 else theory*0.9
        sim_vals.append(sim); theory_vals.append(theory)
    x=np.arange(len(MU_CONDITIONS)); labels=[f'μ={m}' for m in MU_CONDITIONS]
    ax1.bar(x-0.2, sim_vals,    0.4, label='시뮬 측정값', color='#2E75B6')
    ax1.bar(x+0.2, theory_vals, 0.4, label='이론값(F=μN)',  color='#D85A30')
    ax1.set_xticks(x); ax1.set_xticklabels(labels)
    ax1.set_ylabel('이동 거리 (m)')
    ax1.set_title('실험 1: 마찰계수별 이동 거리', fontweight='bold')
    ax1.legend(fontsize=9); ax1.grid(True, alpha=0.3)
    for i,(s,t) in enumerate(zip(sim_vals,theory_vals)):
        err=abs(s-t)/max(t,0.001)*100
        ax1.annotate(f'{err:.1f}%', xy=(x[i],max(s,t)+0.05), ha='center', fontsize=8, color='gray')

    # ── 패널 2: 실험 1 오차율 ──────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    errors=[abs(s-t)/max(t,0.001)*100 for s,t in zip(sim_vals,theory_vals)]
    ax2.bar(labels, errors, color='#534AB7', alpha=0.8)
    ax2.axhline(10, color='red', linestyle='--', linewidth=1.5, label='허용 오차 10%')
    ax2.set_ylabel('오차율 (%)'); ax2.set_title('실험 1: 시뮬-이론 오차율', fontweight='bold')
    ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)

    # ── 패널 3: 실험 2 — 타임스텝별 에너지 오차 ────────────
    ax3 = fig.add_subplot(gs[1, 0])
    colors3=['#2E75B6','#1D7A3A','#D85A30']
    for dt,color in zip(DT_CONDITIONS,colors3):
        L,g=1.0,GRAVITY; theta,omega=0.5,0.0; energies=[]
        t_arr=np.arange(0,5.0,dt)
        for _ in t_arr:
            E=0.5*(L*omega)**2+g*L*(1-np.cos(theta)); energies.append(E)
            alpha=-(g/L)*theta; theta+=omega*dt; omega+=alpha*dt
        E0=energies[0] if energies[0]>0 else 1e-6
        err_series=[(e-E0)/E0*100 for e in energies]
        ax3.plot(t_arr, err_series, color=color, label=f'Δt={dt}s', linewidth=1.5, alpha=0.85)
    ax3.axhline(0,color='black',linestyle='--',linewidth=1,alpha=0.5)
    ax3.set_xlabel('시간 (s)'); ax3.set_ylabel('에너지 오차 (%)')
    ax3.set_title('실험 2: 타임스텝별 에너지 보존 오차', fontweight='bold')
    ax3.legend(fontsize=9); ax3.grid(True, alpha=0.3)

    # ── 패널 4: 실험 3 — 노이즈 설정 vs 측정 std ───────────
    ax4 = fig.add_subplot(gs[1, 1])
    meas_stds=[]
    for sigma in SIGMA_CONDITIONS:
        bag=os.path.join(RESULTS_DIR, f'imu_sigma{sigma}')
        data=_load_or_demo(bag, load_imu_angular_z,
                           lambda s_=sigma: np.random.normal(0, max(s_,1e-9), 3000))
        meas_stds.append(float(np.std(data)) if len(data)>0 else sigma)
    ideal=np.linspace(0, max(SIGMA_CONDITIONS)+0.02, 100)
    ax4.plot(ideal, ideal, 'k--', linewidth=1.5, label='이상: 설정=측정')
    ax4.scatter(SIGMA_CONDITIONS, meas_stds, s=180, color='#2E75B6', zorder=5, label='측정 std')
    for x_pt,y_pt in zip(SIGMA_CONDITIONS,meas_stds):
        ax4.annotate(f'σ={x_pt}', (x_pt,y_pt), textcoords='offset points', xytext=(6,6), fontsize=8)
    ax4.set_xlabel('설정 σ (rad/s)'); ax4.set_ylabel('측정 표준편차 (rad/s)')
    ax4.set_title('실험 3: IMU 노이즈 설정값 vs 측정', fontweight='bold')
    ax4.legend(fontsize=9); ax4.grid(True, alpha=0.3)

    fig.suptitle(
        'M13 물리 시뮬레이션 3개 실험 종합 결과\n'
        'Sim-to-Real 갭 원인: ① 마찰 불일치  ② 수치 오차  ③ 센서 노이즈',
        fontsize=13, fontweight='bold', y=1.02
    )
    return fig


def main():
    print('=== M13 종합 시각화 ===\n')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    has_real=any(os.path.exists(os.path.join(RESULTS_DIR,f'friction_mu{mu}')) for mu in MU_CONDITIONS)
    if not has_real:
        print('[데모 모드] bag 없이 이론값 기반 그래프 생성')
    fig = build_summary_figure()
    out = os.path.join(RESULTS_DIR, 'm13_summary.png')
    fig.savefig(out, dpi=150, bbox_inches='tight')
    print(f'저장 완료: {out}\n→ 리포트 5.1절에 이 그래프를 삽입하세요')

if __name__ == '__main__':
    main()
