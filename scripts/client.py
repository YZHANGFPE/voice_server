#!/usr/bin/env python
import sys
import rospy
from voice_server.srv import Voice

def voice_client(Sen):
    rospy.wait_for_service('voice')
    try:
        speak = rospy.ServiceProxy('voice', Voice)
        speak(Sen)
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

if __name__ == "__main__":
    voice_client(sys.argv[1])
