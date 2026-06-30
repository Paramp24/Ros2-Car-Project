#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import math

from sensor_msgs.msg import LaserScan
# Changed from Twist to TwistStamped
from geometry_msgs.msg import TwistStamped 

class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')

        # Changed publisher type to TwistStamped
        self.publisher_ = self.create_publisher(
            TwistStamped,
            '/diff_cont/cmd_vel',
            10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)
        self.get_logger().info('Rule-based Obstacle Avoidance (TwistStamped) Test Node Started!')

    def scan_callback(self, msg):
        front_ranges = []

        for r in msg.ranges[60:120]:
            if r != float('inf') and not math.isnan(r):
                front_ranges.append(r)

        if len(front_ranges) == 0:
            min_distance = 999.0
        else:
            min_distance = min(front_ranges)

        # Create a Stamped message wrapper
        cmd = TwistStamped()
        
        # Populate the mandatory time stamp header
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        if min_distance > 0.25:
            self.get_logger().info(f'Clear path! Distance: {min_distance:.2f}m -> Driving Forward')
            cmd.twist.linear.x = 0.2
            cmd.twist.angular.z = 0.0
        else:
            self.get_logger().warn(f'Obstacle detected! Distance: {min_distance:.2f}m -> Turning')
            cmd.twist.linear.x = 0.0
            cmd.twist.angular.z = 0.5


        self.publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()