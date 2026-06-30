import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():

    pkg_name = 'articubot_one'

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(pkg_name),
                'launch',
                'rsp.launch.py'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    world_path = os.path.join(
        get_package_share_directory(pkg_name),
        'worlds',
        'cone.sdf'
    )
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            # CHANGED: Swapped ogre2 to ogre to allow software rendering on Apple Silicon
            'gz_args': f'-r {world_path} --render-engine ogre'
        }.items()
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'articubot'
                ],
                output='screen'
            )
        ]
    )

    spawn_joint_broad = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_broad',
                    '--controller-manager', '/controller_manager',
                    '--controller-manager-timeout', '60',
                    '--switch-timeout', '60'
                ],
                output='screen'
            )
        ]
    )

    spawn_diff_cont = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'diff_cont',
                    '--controller-manager', '/controller_manager',
                    '--controller-manager-timeout', '60',
                    '--switch-timeout', '60'
                ],
                output='screen'
            )
        ]
    )

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image'
        ],
        output='screen'
    )

    obstacle_avoidance_node = Node(
        package='articubot_one',
        executable='obstacle_avoidance.py',
        name='obstacle_avoidance',
        output='screen',
        parameters=[{'use_sim_time': True}] # Crucial so it syncs perfectly with Gazebo's clock
    )


    return LaunchDescription([
        # Forces software rendering environment variable for everything in this launch file
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE', '1'),
        rsp,
        gazebo,
        clock_bridge,
        spawn_robot,
        spawn_joint_broad,
        spawn_diff_cont,
        scan_bridge,
        obstacle_avoidance_node
    ])