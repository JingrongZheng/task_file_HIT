import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import numpy as np

class SubNode(Node):

    def __init__(self,name):
        super().__init__(name)
        self.suber=self.create_subscription(Image,"apple",self.suberCallback,10)
        self.puber=self.create_publisher(Image,"ProcessedApple",10)
        self.bridge=CvBridge()

    def processing(self,image):
        P=image.copy()
        Phsv=cv2.cvtColor(P,cv2.COLOR_BGR2HSV)

        k=np.ones((5,5),np.uint8)
        Phsv=cv2.morphologyEx(Phsv,cv2.MORPH_OPEN,k)

        lower_red = np.array([0, 43, 46])
        upper_red = np.array([10, 255, 255])
        Pres1=cv2.inRange(Phsv,lower_red,upper_red)

        lower_red = np.array([156, 43, 46])
        upper_red = np.array([180, 255, 255])
        Pres2=cv2.inRange(Phsv,lower_red,upper_red)
        #
        Pres=Pres1+Pres2
        Pres=cv2.erode(Pres,k,iterations=3)
        k=np.ones((7,7),np.uint8)
        Pres=cv2.dilate(Pres,k,iterations=5)

        #sobel
        sobelx=cv2.Sobel(Pres,cv2.CV_64F,1,0,ksize=11)
        sobelx=cv2.convertScaleAbs(sobelx)
        sobely=cv2.Sobel(Pres,cv2.CV_64F,0,1,ksize=11)
        sobely=cv2.convertScaleAbs(sobely)
        sobelxy=cv2.addWeighted(sobelx,0.5,sobely,0.5,0)
        Pxy=cv2.convertScaleAbs(sobelxy)

        #draw
        Pcc=P.copy()
        c,h=cv2.findContours(Pxy,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt=c[11]
        (x,y,w,h)=cv2.boundingRect(cnt)
        cv2.rectangle(Pcc,(x,y),(x+w,y+h),(10,240,80),17)
        
        return Pcc


    def suberCallback(self,photo):
        self.get_logger().info("Processing...")
        newphoto=self.bridge.imgmsg_to_cv2(photo,"bgr8")
        res=self.processing(newphoto)
        '''cv2.namedWindow("apple",0)
        cv2.resizeWindow("apple",500,300)
        cv2.imshow("apple",res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''
        rosphoto=self.bridge.cv2_to_imgmsg(res,"bgr8")

        rosphoto.header.stamp=self.get_clock().now().to_msg()
        rosphoto.header.frame_id='Processed'
        #self.puber.publish(rosphoto)
        self.get_logger().info("Found the apple.")


        self.img=rosphoto
        self.time_period=2
        self.timer=self.create_timer(self.time_period,self.timerCallback)

    def timerCallback(self):
        self.puber.publish(self.img)
        self.get_logger().info("Publishing")


def main(args=None):
    rclpy.init(args=args)
    sub_node=SubNode("Sub")
    rclpy.spin(sub_node)
    rclpy.shutdown()