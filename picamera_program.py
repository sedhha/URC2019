import cv2
import numpy as np
import socket
import sys
import pickle
import struct ### new code
from PIL import Image
import argparse
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
#extensive for picamera
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# clientsocket.connect(('192.168.1.125',8089))
clientsocket.connect(('192.168.43.217',8089)) #laptop IP
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array
	print(sys.getsizeof(image))
	data = cv2.imencode('.jpg',image)[1].tostring()
	a = struct.pack("q", len(data))
	payload_size = struct.calcsize("q")
	packed_msg_size = a[:payload_size]
	msg_size = struct.unpack("q", packed_msg_size)
	print(msg_size)
	print(sys.getsizeof(data))
	clientsocket.sendall(struct.pack("q", len(data))+data)
	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
	if key == ord("q"):
		break
