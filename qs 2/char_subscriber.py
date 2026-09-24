import rclpy
from rclpy.node import Node
from std_msgs.msg import Char


class SubscriberNode(Node):

    def __init__(self):
        super().__init__('subscriber_node')

        self.subscription = self.create_subscription(
            Char,
            'character_topic',
            self.listener_callback,
            10
        )

        self.subscription

    def listener_callback(self, message):

        character = chr(message.data)

        self.get_logger().info(
            'Subscriber node received: "%s"' % character
        )


def main(args=None):

    rclpy.init(args=args)

    subscriber_node = SubscriberNode()

    rclpy.spin(subscriber_node)

    subscriber_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()