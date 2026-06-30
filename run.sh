#!/bin/bash
# run.sh — M13 실험 전체 실행 스크립트
# 사용: bash run.sh [python|exp1|exp2|exp3|all|verify]
# 반드시 ND1_M13_PBL/ 루트에서 실행하세요
set -e
MODE=${1:-python}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source /opt/ros/humble/setup.bash 2>/dev/null || true
echo "=== ND1 M13 run.sh | mode=${MODE} ==="

case "$MODE" in
  python)
    echo "[Track A] Pure Python 실험 (평가용)"
    python3 python/exp1_euler_rk4.py
    python3 python/exp2_friction_slope.py
    python3 python/exp3_inertia_gap.py
    echo "=== Track A 완료 — results/ 확인하세요 ==="
    ;;
  verify)
    echo "[Track B] 환경 검증 — 교재 4.4절 기준"
    detect_gazebo() {
      if command -v ign &>/dev/null; then
        V=$(ign gazebo --version 2>/dev/null | grep -oP 'version \K[0-9]+' | head -1)
        [[ -n "$V" ]] && echo "ign" && return
      fi
      if command -v gz &>/dev/null; then
        V=$(gz sim --version 2>/dev/null | grep -oP 'version \K[0-9]+' | head -1)
        [[ -n "$V" ]] && echo "gz" && return
      fi
      echo "none"
    }
    GZ=$(detect_gazebo)
    PASS=0; FAIL=0
    echo ""
    echo "▶ 항목 1 — Gazebo 설치"
    case "$GZ" in
      ign) V=$(ign gazebo --version 2>/dev/null | grep -oP 'version \K[0-9.]+' | head -1)
           M=$(echo "$V" | cut -d. -f1)
           [[ "$M" == "6" ]] && echo "  ✅ Fortress $V" || echo "  ⚠️  Gazebo $V (Fortress=6.x 권장)"
           PASS=$((PASS+1)) ;;
      gz)  V=$(gz sim --version 2>/dev/null | grep -oP 'version \K[0-9.]+' | head -1)
           echo "  ⚠️  gz sim $V (교재는 ign gazebo 기준)"
           PASS=$((PASS+1)) ;;
      none) echo "  ❌ Gazebo 미설치"; FAIL=$((FAIL+1)) ;;
    esac
    [[ -n "$IGN_GAZEBO_RESOURCE_PATH" ]] && echo "  ✅ IGN_GAZEBO_RESOURCE_PATH 설정됨" || echo "  ❌ IGN_GAZEBO_RESOURCE_PATH 미설정 (교재 4.2절 참조)"
    ros2 pkg list 2>/dev/null | grep -q turtlebot4_ignition_bringup && echo "  ✅ turtlebot4 패키지 OK" || echo "  ❌ turtlebot4 미설치: sudo apt install ros-humble-turtlebot4-simulator"
    echo ""
    echo "▶ 항목 2 — ROS2 환경"
    command -v ros2 &>/dev/null && { echo "  ✅ ROS2 설치됨"; PASS=$((PASS+1)); } || { echo "  ❌ ROS2 없음"; FAIL=$((FAIL+1)); }
    echo ""
    echo "▶ 항목 3 — 패키지 구조"
    ALL_OK=true
    for d in python scripts src worlds results; do
      [[ -d "$SCRIPT_DIR/$d" ]] && echo "  ✅ $d/" || { echo "  ❌ $d/ 없음"; ALL_OK=false; }
    done
    [[ -f "$SCRIPT_DIR/src/sdf_utils.py" ]] && echo "  ✅ src/sdf_utils.py" || { echo "  ❌ sdf_utils.py 없음"; ALL_OK=false; }
    $ALL_OK && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
    echo ""
    echo "▶ 항목 4 — Python 라이브러리"
    PY_OK=true
    for lib in numpy scipy matplotlib; do
      python3 -c "import $lib" 2>/dev/null && echo "  ✅ $lib" || { echo "  ❌ $lib 없음"; PY_OK=false; }
    done
    python3 -c "import rosbags" 2>/dev/null && echo "  ✅ rosbags" || echo "  ⚠️  rosbags 없음 (Track A 불필요, Track B 필요)"
    $PY_OK && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
    echo ""
    echo "결과: ${PASS}/4 통과 | 실패: ${FAIL}"
    [[ $FAIL -eq 0 ]] && echo "✅ 모두 통과 — 실습 시작 가능" || echo "❌ 실패 항목 수정 후 재실행"
    ;;
  exp1) python3 scripts/exp1_friction.py ;;
  exp2) python3 scripts/exp2_timestep.py ;;
  exp3) python3 scripts/exp3_noise.py ;;
  all)
    echo "[Track B] Gazebo 전체 분석"
    python3 scripts/exp1_friction.py
    python3 scripts/exp2_timestep.py
    python3 scripts/exp3_noise.py
    python3 scripts/visualize.py
    echo "=== Track B 완료 — results/ 확인하세요 ==="
    ;;
  *)
    echo "사용법: bash run.sh [python|exp1|exp2|exp3|all|verify]"
    echo "  python  — Track A: Pure Python 실험 (평가용)"
    echo "  verify  — Track B 환경 검증"
    echo "  exp1/2/3 — Track B 개별 분석"
    echo "  all     — Track B 전체 분석"
    exit 1 ;;
esac
