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
    '''
    with open('calibration_matrix.yaml') as data:
        data_dict = yaml.load(data, Loader=yaml.FullLoader)

    Kd=np.array(data_dict['K'])
    Dd=np.array(data_dict['D'])
    '''
    
    
    windowName = "Preview"
    cv2.namedWindow(windowName)
    cap = cv2.VideoCapture('video_grid.h264')
    inital_frame = 5
    fps_count = 1
    #cap.set(3, 1024)
    #cap.set(4, 576)
    
    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()
        #Make the code only start getting points after intial_frame
        if fps_count >= inital_frame and fps_count < 298:

            #find points of the first frame
            if fps_count - inital_frame == 0:
                intersectionPoints, totalGrid = vidProc.findInitPoints(frame)
                D_xy_mean_total = 0
            

            #cimg = calibrateFisheye.undist(frame,Kd,Dd)
            #lines,cimg=vidProc.binaryGridDetection(frame)
            
            intersectionPoints1,cimg = vidProc.findIntPoints(frame)
            totalGrid, totalGridc, D_xy_mean_total = cellSum.continuousGrid(intersectionPoints, np.asarray(intersectionPoints1), totalGrid,totalGrid, intersectionPoints,np.asarray(intersectionPoints1),0,0,D_xy_mean_total)
            
            #make the mew frame the old for the next iteration of cycle
            intersectionPoints = np.asarray(intersectionPoints1)
            
            #cimg = vidProc.findCircles(frame)
            cv2.imshow(windowName, frame)
            cv2.imshow("frame", cimg)
            if cv2.waitKey(1) == 27:
                break
        fps_count +=1
        print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    cellSum.plotIntPoints(totalGrid)
    
main()
