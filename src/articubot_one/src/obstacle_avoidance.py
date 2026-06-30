#!/usr/bin/env python3

import os
import math
import numpy as np
import gym
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback

class ObstacleAvoidanceML(gym.Env, Node):

    def __init__(self):
        Node.__init__(self, 'obstacle_avoidance')
        
        self.publisher_ = self.create_publisher(Twist, '/diff_cont/cmd_vel', 10)

        self.teleport_pub = self.create_publisher(Pose, '/world/empty/set_pose', 10)

        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        self.observation_space = gym.spaces.Box(low=0.0, high=10.0, shape=(10,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(3)
        
        self.latest_ranges = [10.0] * 10
        self.get_logger().info('ML Obstacle Avoidance Environment with Auto-Reset Ready!')

    def scan_callback(self, msg):
        front_ranges = []
        for r in msg.ranges[85:95]:
            if r != float('inf') and not math.isnan(r):
                front_ranges.append(r)
            else:
                front_ranges.append(10.0)
        
        if len(front_ranges) == 10:
            self.latest_ranges = front_ranges

    def reset(self):

        stop_cmd = Twist()
        self.publisher_.publish(stop_cmd)

        reset_pose = Pose()
        reset_pose.position = Point(x=0.0, y=0.0, z=0.0)
        reset_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self.teleport_pub.publish(reset_pose)

        import time
        time.sleep(0.1)

        rclpy.spin_once(self, timeout_sec=0.05)
        return np.array(self.latest_ranges, dtype=np.float32)

    def step(self, action):
        cmd = Twist()
        if action == 0:     
            cmd.linear.x = 0.2
            cmd.angular.z = 0.0
        elif action == 1:   
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5
        elif action == 2:   
            cmd.linear.x = 0.0
            cmd.angular.z = -0.5

        self.publisher_.publish(cmd)
        rclpy.spin_once(self, timeout_sec=0.01)
        
        obs = np.array(self.latest_ranges, dtype=np.float32)
        
        reward = 0.1 if min(obs) > 0.5 else -2.0  
        done = True if min(obs) <= 0.2 else False
        info = {}
            
        return obs, reward, done, info


def main(args=None):
    rclpy.init(args=args)

    home_dir = os.path.expanduser('~')
    base_path = os.path.join(home_dir, "Tutorial/src/articubot_one/src")
    checkpoint_dir = os.path.join(base_path, "ml_navigation_checkpoints")

    node = ObstacleAvoidanceML()

    checkpoint_callback = CheckpointCallback(
        save_freq=5000,
        save_path=checkpoint_dir,
        name_prefix='obstacle_avoid_model'
    )

    model = PPO("MlpPolicy", node, verbose=1, learning_rate=0.0003)

    print("Spawning Machine Learning loop... Watch the robot auto-teleport on crash!")
    try:
        model.learn(total_timesteps=100000, callback=checkpoint_callback)
        model.save(os.path.join(base_path, "final_obstacle_avoidance_brain"))
    except KeyboardInterrupt:
        print("\nTraining manually stopped.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()