import cv2
import numpy as np
import yaml
import vidProc
from scipy import ndimage



with open('calibration_matrix.yaml') as data:
    data_dict = yaml.load(data, Loader=yaml.FullLoader)

cap = cv2.VideoCapture('gridRotation2.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()
    dst=vidProc.undist(frame,data_dict)
    cv2.imshow('frame',dst)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

