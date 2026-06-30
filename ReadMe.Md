colcon build --symlink-install
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch articubot_one launch_sim.launch.py