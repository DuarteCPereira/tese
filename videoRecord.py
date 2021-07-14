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
    camera.start_recording('rec.h264')
    sleep(t)
    camera.stop_recording()
    camera.stop_preview()
    
    command = "MP4Box -add rec.h264 " + name
    call([command], shell=True)
