# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile, qos_profile_sensor_data, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# TODO Part 3: Import message types needed: 
    # For sending velocity commands to the robot: Twist
    # For the sensors: Imu, LaserScan, and Odometry
# Check the online documentation to fill in the lines below
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, LaserScan
from nav_msgs.msg import Odometry

from rclpy.time import Time

# You may add any other imports you may need/want to use below
# import ...
import math
import os


CIRCLE=0; SPIRAL=1; ACC_LINE=2
motion_types=['circle', 'spiral', 'line']

class motion_executioner(Node):
    
    def __init__(self, motion_type=0):
        
        super().__init__("motion_types")
        
        self.type=motion_type
        
        self.radius_=0.0
        
        self.successful_init=False
        self.imu_initialized=False
        self.odom_initialized=False
        self.laser_initialized=False

        # simple internal state for motion generation
        self.dt = 0.1  # timer period seconds
        self.t  = 0.0  # time accumulator
        self.lin_v = 0.0
        
        # TODO Part 3: Create a publisher to send velocity commands by setting the proper parameters in (...)
        self.vel_publisher=self.create_publisher(Twist, '/cmd_vel', 10)
                
        # loggers
        self.imu_logger=Logger('imu_content_'+str(motion_types[motion_type])+'.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger=Logger('odom_content_'+str(motion_types[motion_type])+'.csv', headers=["x","y","th", "stamp"])
        self.laser_logger=Logger('laser_content_'+str(motion_types[motion_type])+'.csv', headers=["ranges", "angle_increment", "stamp"])
        
        # TODO Part 3: Create the QoS profile by setting the proper parameters in (...)
        qos=QoSProfile(
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.VOLATILE
        )

        # TODO Part 5: Create below the subscription to the topics corresponding to the respective sensors
        # IMU subscription
        self.create_subscription(Imu, '/imu', self.imu_callback, qos_profile_sensor_data)
        
        # ENCODER subscription
        # (Odometry provides x,y,theta from wheel encoders + base odom)
        self.create_subscription(Odometry, '/odom', self.odom_callback, qos)
        
        # LaserScan subscription 
        self.create_subscription(LaserScan, '/scan', self.laser_callback, qos_profile_sensor_data)
        
        self.create_timer(self.dt, self.timer_callback)


    # TODO Part 5: Callback functions: complete the callback functions of the three sensors to log the proper data.
    # To also log the time you need to use the rclpy Time class, each ros msg will come with a header, and then
    # inside the header you have a stamp that has the time in seconds and nanoseconds, you should log it in nanoseconds as 
    # such: Time.from_msg(imu_msg.header.stamp).nanoseconds
    # You can save the needed fields into a list, and pass the list to the log_values function in utilities.py

    def imu_callback(self, imu_msg: Imu):
        # log imu msgs
        try:
            acc_x = float(imu_msg.linear_acceleration.x)
            acc_y = float(imu_msg.linear_acceleration.y)
            ang_z = float(imu_msg.angular_velocity.z)
            stamp_ns = Time.from_msg(imu_msg.header.stamp).nanoseconds
            self.imu_logger.log_values([acc_x, acc_y, ang_z, stamp_ns])
            self.imu_initialized = True
        except Exception as e:
            self.get_logger().warn(f"IMU callback error: {e}")
        
    def odom_callback(self, odom_msg: Odometry):
        
        # log odom msgs
        try:
            x = float(odom_msg.pose.pose.position.x)
            y = float(odom_msg.pose.pose.position.y)
            q = odom_msg.pose.pose.orientation
            th = float(euler_from_quaternion([q.x, q.y, q.z, q.w]))  # yaw
            stamp_ns = Time.from_msg(odom_msg.header.stamp).nanoseconds
            self.odom_logger.log_values([x, y, th, stamp_ns])
            self.odom_initialized = True
        except Exception as e:
            self.get_logger().warn(f"Odom callback error: {e}")
                
    def laser_callback(self, laser_msg: LaserScan):
        
        # log laser msgs with position msg at that time
        try:
            # Store ranges as a single semicolon-separated string to keep one CSV cell
            ranges_str = ";".join([f"{r}" for r in laser_msg.ranges])
            angle_increment = float(laser_msg.angle_increment)
            stamp_ns = Time.from_msg(laser_msg.header.stamp).nanoseconds
            self.laser_logger.log_values([ranges_str, angle_increment, stamp_ns])
            self.laser_initialized = True
        except Exception as e:
            self.get_logger().warn(f"Laser callback error: {e}")
                
    def timer_callback(self):
        
        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init=True
            
        if not self.successful_init:
            return
        
        cmd_vel_msg=Twist()
        
        if self.type==CIRCLE:
            cmd_vel_msg=self.make_circular_twist()
        
        elif self.type==SPIRAL:
            cmd_vel_msg=self.make_spiral_twist()
                        
        elif self.type==ACC_LINE:
            cmd_vel_msg=self.make_acc_line_twist()

            
        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit 

        self.vel_publisher.publish(cmd_vel_msg)
        self.t += self.dt  # advance internal time
        
    
    # TODO Part 4: Motion functions: complete the functions to generate the proper messages corresponding to the desired motions of the robot

    def make_circular_twist(self):
        
        msg=Twist()
        # fill up the twist msg for circular motion
        msg.linear.x = 0.15
        msg.angular.z = 0.30
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        return msg

    def make_spiral_twist(self):
        msg=Twist()
        # fill up the twist msg for spiral motion
        self.radius_ = min(self.radius_ + 0.01, 1.25)  # meters
        v = 0.15  # m/s
        # Avoid division by zero; start with a small radius then grow.
        effective_r = max(self.radius_, 0.05)
        omega = v / effective_r  # ω = v / r
        msg.linear.x = v
        msg.angular.z = omega
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        return msg
    
    def make_acc_line_twist(self):
        msg=Twist()
        # fill up the twist msg for line motion
        a = 0.25
        self.lin_v = min(self.lin_v + a * self.dt, 0.35)
        msg.linear.x = self.lin_v
        msg.angular.z = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        return msg

import argparse

if __name__=="__main__":
    

    argParser=argparse.ArgumentParser(description="input the motion type")


    argParser.add_argument("--motion", type=str, default="circle")



    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":

        ME=motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME=motion_executioner(motion_type=ACC_LINE)

    elif args.motion.lower() =="spiral":
        ME=motion_executioner(motion_type=SPIRAL)

    else:
        print(f"we don't have {args.motion.lower()} motion type")


    
    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
