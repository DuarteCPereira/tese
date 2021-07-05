import cv2
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt
import vidProc
import cellSum
import grid_map

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
    cap.release()
    '''
    
    windowName = "Preview"
    #cv2.namedWindow(windowName)
    cap = cv2.VideoCapture('10mm_100mm_min_yy.mp4')
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame = length
    fps_count = 1
    inital_frame = 100
    #last_frame = 400
    #cap.set(3, 1024)
    #cap.set(4, 576)
    

    if cap.isOpened():
        ret, frame = cap.read()
        
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()
        #Make the code only start getting points after intial_frame
        if fps_count >=4 and fps_count < last_frame and fps_count % 1 == 0:
            centerPoint = np.array([]).reshape(0, 2)
            midFrame = np.flip(np.asarray(frame.shape[:2])/2)
            intersectionPoints1, cimg, horizontal, vertical, img_bwa = vidProc.findIntPoints(frame, midFrame)
            print('IP!', len(intersectionPoints1))
            if fps_count == 4:
                intersectionPoints = intersectionPoints1

            if fps_count >=5:
                if len(intersectionPoints1) < len(intersectionPoints)-5:
                    print('frame bugado')
                else:
                    intersectionPoints = intersectionPoints1        
                
            cv2.imshow(windowName, cimg)
            
            if cv2.waitKey(1) == 27:
                break
        fps_count += 1
        print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    

main()