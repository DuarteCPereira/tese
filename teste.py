import cv2
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt
import vidProc
import calibrateFisheye
import cellSum

#Uncoment if in need to calculate new parameters
'''
#Calling of function that calculates calibration parameters from images on /CalibrationImages
#calibrateFisheye.getCalibParameters()
'''


def main():
    
    #Import calibration 
    with open('calibration_matrix.yaml') as data:
        data_dict = yaml.load(data, Loader=yaml.FullLoader)

    Kd=np.array(data_dict['K'])
    Dd=np.array(data_dict['D'])
    
    #Inicialização dos pontos do frame 0
    intersectionPoints = np.array([[0.1,0.1]])
    totalGrid = intersectionPoints
    D_xy_mean_total = 0
    
    
    windowName = "Preview"
    cv2.namedWindow(windowName)
    cap = cv2.VideoCapture(0)
    cap.set(3, 1024)
    cap.set(4, 576)
    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()
        #cimg = calibrateFisheye.undist(frame,Kd,Dd)
        
        #lines,cimg=vidProc.binaryGridDetection(frame)
        intersectionPoints1,cimg = vidProc.findIntPoints(frame)
        #print(intersectionPoints1)
        totalGrid, totalGridc, D_xy_mean_total=cellSum.continuousGrid(intersectionPoints,np.asarray(intersectionPoints1),totalGrid,totalGrid,intersectionPoints,np.asarray(intersectionPoints1),0,0,D_xy_mean_total)
        
        
        #cimg = vidProc.findCircles(frame)
        cv2.imshow(windowName, frame)
        cv2.imshow("frame", cimg)
        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()
    cap.release()
    
main()
