#!/bin/bash
cd ~/ND1_M13_PBL
source /opt/ros/humble/setup.bash
source install/setup.bash
export IGN_GAZEBO_RESOURCE_PATH=$PWD/worlds:$PWD/models:$IGN_GAZEBO_RESOURCE_PATH
ign gazebo worlds/noise_test.sdf
