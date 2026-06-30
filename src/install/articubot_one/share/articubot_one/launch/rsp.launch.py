import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory('articubot_one')
    xacro_file = os.path.join(pkg_path, 'description', 'robot_urdf.xacro')

    robot_description = {
        'robot_description': Command(['xacro ', xacro_file])
    }

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[robot_description, 
                        {'use_sim_time': True}]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        )
    ])
