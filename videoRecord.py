from picamera import PiCamera
from time import sleep

def recordVid(time, name):
	camera = PiCamera()

	camera.start_preview()
	camera.start_recording(name)
	sleep(time)
	camera.stop_recording()
	camera.stop_preview()

if __name__ == '__main__':
