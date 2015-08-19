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
from voice_server.srv import *

class VoiceServer:

    def __init__(self, local):
        self.service = rospy.Service('voice', Voice, self.handle_voice_requests)
        rospy.loginfo("Ready to use the voice server")
        rospack = rospkg.RosPack()
        self.mp3_folder = rospack.get_path('voice_server') + "/mp3/"
        self.dict = {}
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.loop = gobject.MainLoop()
        self.playing = False
        self.local = local
        if not self.local: 
            rospy.loginfo("Use web api")
        else: 
            rospy.loginfo("Use local stream file")
        with open(self.mp3_folder+'dict.yaml', 'r') as f:
            self.dict = yaml.load(f)

    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            rospy.loginfo("finish playing")
            self.playing = False
            self.player.set_state(gst.STATE_NULL)
            self.loop.quit()
        elif message.type == gst.MESSAGE_ERROR:
            gerr, dbgmsg = message.parse_error()
            self.player.set_state(gst.STATE_NULL)
            self.loop.quit()
            sys.exit("error (%s:%d '%s'): %s" % (gerr.domain, gerr.code, gerr.message, dbgmsg))
        


    def handle_voice_requests(self, req):
        self.speak(message = req.msg)
        resp = VoiceResponse(1)
        return resp


    def speak(self, message):

        if not self.local: 
            music_stream_uri = 'http://translate.google.com/translate_tts?tl=en&q=' + message
        else: 
            if not message in self.dict:
                string = 'hello_baxter'
                rospy.logwarn("The local stream file is not found")
            else:
                string = str(self.dict[message])
            music_stream_uri = 'file://' + self.mp3_folder + string + '.mp3'

        self.run()
        self.playing = True
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property('uri',music_stream_uri)
        self.player.set_state(gst.STATE_PLAYING)
        self.block()

    def run(self):
        """Start a new thread for the player.

        Call this function before trying to play any music with
        play_file() or play().
        """
        # If we don't use the MainLoop, messages are never sent.
        gobject.threads_init()
        def start():
            self.loop.run()
        thread.start_new_thread(start, ())

    def block(self):
        """Block until playing finishes."""
        while self.playing:
            time.sleep(1)


        
def main():

    
    if len(sys.argv) < 2:
        local = False
    else:
        if sys.argv[1] == '--local': local = True
        else: local = False

    rospy.init_node('voice_server', anonymous=True)
    vs = VoiceServer(local)
    rospy.spin()
    

if __name__=='__main__':

    sys.exit(main())