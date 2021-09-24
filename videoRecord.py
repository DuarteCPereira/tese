#import picamera
from time import sleep
from subprocess import call
import os


def recordVid(t, name):
    b = './' + name
    a = os.path.isfile(b)
    if a:
        os.remove(b)

    camera = picamera. PiCamera()
    
    camera.resolution = (480, 320)
    camera.framerate = 10
    camera.start_preview()
    camera.start_recording(output='rec.h264', splitter_port=2)
    sleep(t)
    camera.stop_recording(2)
    camera.stop_preview()
    camera.close()
    
    command = "MP4Box -add rec.h264 " + name
    call([command], shell=True)
    
#recordVid(20, "Y_mov_skew.mp4")
