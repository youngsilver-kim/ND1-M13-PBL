#!/bin/bash
cd ~/ND1_M13_PBL
source /opt/ros/humble/setup.bash
source install/setup.bash
export IGN_GAZEBO_RESOURCE_PATH=$PWD/worlds:$PWD/models:$IGN_GAZEBO_RESOURCE_PATH

echo "=== Gazebo friction_test 실행 ==="
ign gazebo worlds/friction_test.sdf
