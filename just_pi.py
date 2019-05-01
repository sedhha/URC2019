import cv2
import numpy as np
import socket
import sys
import pickle
import struct ### new code
from PIL import Image
import argparse
import time

#COMMAND python3 send_feeds.py --port 1
#DONT FORGET TO CHANGE THE IP ACCORDINGLY

ap=argparse.ArgumentParser()
ap.add_argument("-i","--port",required=True,help="Name of camera port")
args=vars(ap.parse_args())
cap=cv2.VideoCapture(int(args["port"]))
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# clientsocket.connect(('192.168.1.125',8089))
clientsocket.connect(('192.168.137.1',8089))

while True:
    ret,frame=cap.read()
    print(sys.getsizeof(frame))
    data = cv2.imencode('.jpg',frame)[1].tostring()
    # data = pickle.dumps(frame, protocol=1) ### new code
    # data = np.frombuffer(frame.tobytes(), dtype="B").reshape((640,480,3),)
    print(sys.getsizeof(data))
    a = struct.pack("q", len(data))
    payload_size = struct.calcsize("q")
    packed_msg_size = a[:payload_size]
    msg_size = struct.unpack("q", packed_msg_size)
    print(msg_size)
    clientsocket.sendall(struct.pack("q", len(data))+data) ### new code
    #time.sleep(0.05)
