import cv2
import numpy as np

img=cv2.imread('1.jpg',cv2.IMREAD_COLOR)

px=img[55,55]
print(px)
roi=img[100:150,100:150]
print(roi)
