import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from turtlesim.srv import Spawn
from turtlesim.srv import TeleportAbsolute


class RobotDance(Node):

    def __init__(self):
        super().__init__('robot_dance')

        # -------------------------
        # TF broadcaster
        # -------------------------
        self.tf_broadcaster = TransformBroadcaster(self)

        # -------------------------
        # Problem parameters
        # -------------------------
        self.R = 5.0
        self.omega = 0.40
        self.T = 8.0

        # -------------------------
        # Display parameters
        # -------------------------
        # turtlesim coordinates are roughly 0 to 11
        #
        # Our mathematical world has negative coordinates,
        # so we shift and scale it for visualization.
        self.display_scale = 0.6
        self.display_x_offset = 5.5
        self.display_y_offset = 5.5

        # -------------------------
        # Service clients
        # -------------------------

        self.spawn_client = self.create_client(
            Spawn,
            '/spawn'
        )

        self.teleport_A_client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

        self.teleport_B_client = self.create_client(
            TeleportAbsolute,
            '/turtle2/teleport_absolute'
        )

        # Wait for turtlesim services
        self.get_logger().info('Waiting for turtlesim...')

        self.spawn_client.wait_for_service()

        # Spawn turtle2
        self.spawn_turtle2()

        # Wait until turtle2's teleport service exists
        self.teleport_B_client.wait_for_service()

        # Start time
        self.start_time = self.get_clock().now()

        # 20 Hz update
        self.timer = self.create_timer(
            0.05,
            self.update
        )


    # =====================================================
    # Spawn turtle2
    # =====================================================

    def spawn_turtle2(self):

        request = Spawn.Request()

        request.x = 5.5
        request.y = 5.5
        request.theta = 0.0
        request.name = 'turtle2'

        future = self.spawn_client.call_async(request)

        rclpy.spin_until_future_complete(self, future)

        self.get_logger().info('turtle2 spawned')


    # =====================================================
    # Create TF transform
    # =====================================================

    def create_transform(self, name, x, y, theta):

        transform = TransformStamped()

        transform.header.stamp = (
            self.get_clock().now().to_msg()
        )

        transform.header.frame_id = 'world'
        transform.child_frame_id = name

        # These are the mathematical world coordinates
        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = 0.0

        # Convert planar yaw angle to quaternion
        transform.transform.rotation.x = 0.0
        transform.transform.rotation.y = 0.0

        transform.transform.rotation.z = (
            math.sin(theta / 2.0)
        )

        transform.transform.rotation.w = (
            math.cos(theta / 2.0)
        )

        return transform


    # =====================================================
    # Convert mathematical coordinates to turtlesim
    # =====================================================

    def world_to_turtlesim(self, x, y):

        x_display = (
            self.display_x_offset
            + self.display_scale * x
        )

        y_display = (
            self.display_y_offset
            + self.display_scale * y
        )

        return x_display, y_display


    # =====================================================
    # Teleport turtle
    # =====================================================

    def teleport(self, client, x, y, theta):

        request = TeleportAbsolute.Request()

        request.x = float(x)
        request.y = float(y)
        request.theta = float(theta)

        client.call_async(request)


    # =====================================================
    # Main update
    # =====================================================

    def update(self):

        # Current time since program started
        now = self.get_clock().now()

        t = (
            now - self.start_time
        ).nanoseconds / 1e9


        # =================================================
        # ROBOT A
        # =================================================

        phi = self.omega * t

        x_A = self.R * math.cos(phi)
        y_A = self.R * math.sin(phi)

        # Tangent heading
        theta_A = phi + math.pi / 2.0


        # =================================================
        # ROBOT B
        # =================================================

        s = (2.0 * math.pi / self.T) * t

        x_B = -(
            s + 3.0 * math.sin(s)
        ) / math.sqrt(2.0)

        y_B = (
            s - 3.0 * math.sin(s)
        ) / math.sqrt(2.0)

        # Tangent angle of sine curve
        theta_B = (
            3.0 * math.pi / 4.0
            + math.atan2(
                3.0 * math.cos(s),
                1.0
            )
        )


        # =================================================
        # Broadcast TF
        # =================================================

        tf_A = self.create_transform(
            'robot_A',
            x_A,
            y_A,
            theta_A
        )

        tf_B = self.create_transform(
            'robot_B',
            x_B,
            y_B,
            theta_B
        )

        self.tf_broadcaster.sendTransform(
            [tf_A, tf_B]
        )


        # =================================================
        # Convert to turtlesim display coordinates
        # =================================================

        turtle_A_x, turtle_A_y = (
            self.world_to_turtlesim(
                x_A,
                y_A
            )
        )

        turtle_B_x, turtle_B_y = (
            self.world_to_turtlesim(
                x_B,
                y_B
            )
        )


        # =================================================
        # Move actual turtle sprites
        # =================================================

        self.teleport(
            self.teleport_A_client,
            turtle_A_x,
            turtle_A_y,
            theta_A
        )

        self.teleport(
            self.teleport_B_client,
            turtle_B_x,
            turtle_B_y,
            theta_B
        )


def main(args=None):

    rclpy.init(args=args)

    node = RobotDance()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()