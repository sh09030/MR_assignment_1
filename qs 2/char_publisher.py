import rclpy
from rclpy.node import Node
from std_msgs.msg import Char


class PublisherNode(Node):

    def __init__(self):
        super().__init__('publisher_node')

        self.publisher_ = self.create_publisher(
            Char,
            'character_topic',
            10
        )

    def publish_character(self):

        user_input = input('Enter a character: ')

        if len(user_input) != 1:
            print('Please enter only one character.')
            return

        message = Char()
        message.data = ord(user_input)

        self.publisher_.publish(message)

        self.get_logger().info(
            'Publisher node is publishing: "%s"' % user_input
        )


def main(args=None):

    rclpy.init(args=args)

    publisher_node = PublisherNode()

    try:
        while rclpy.ok():
            publisher_node.publish_character()

    except KeyboardInterrupt:
        pass

    publisher_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()