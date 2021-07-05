from picamera import PiCamera
from time import sleep
from subprocess import call

def recordVid(time, name):
	camera = PiCamera()

	camera.start_preview()
	camera.start_recording("rec.h264")
	sleep(time)
	camera.stop_recording()
	camera.stop_preview()

	command = "MP4Box -add rec.h264" + name
	call([command], shell=True)
if __name__ == '__main__':
