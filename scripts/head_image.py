#!/usr/bin/env python
import rospy
import roscpp
import pygst
import gobject
import thread
import gst
import sys
import rospkg
import yaml
import time
import argparse
from std_msgs.msg import String
from subprocess import call
import os




def callback(data):
    rospy.loginfo("The requested image is %s", data.data)
    string = "rosrun baxter_examples xdisplay_image.py --file=`rospack find voice_server`/imgs/" + data.data + ".png"
    os.system(string)
    
def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("head_image", String, callback)

    rospy.loginfo("Head image server started")

    os.system("rosrun baxter_examples xdisplay_image.py --file=`rospack find voice_server`/imgs/black.png")

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
