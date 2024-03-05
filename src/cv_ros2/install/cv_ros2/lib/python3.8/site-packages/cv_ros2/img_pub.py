import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

class PubNode(Node):

    def __init__(self,name,path):
        super.__init__(name)
        self.puber=self.create_publisher(Image,"apple",10)
        self.bridge=CvBridge()
        self.photo_pub(path)


    def photo_pub(self,path):
        img=cv2.imread(path)
        photo=self.bridge.cv2_to_imgmsg(img,"bgr8")
        photo.header.stamp=self.get_clock().now().to_msg()
        photo.header.frame_id='Origin'

        self.puber.publish(photo)
        self.get_logger().info("Now published a photo.")

def main(args=None):
    rclpy.init(args=args)
    PATH=R"/home/ros2zjr/resource/apple.jpg"
    pub_node=PubNode("Pub",PATH)
    rclpy.spin(pub_node)
    rclpy.shutdown()
