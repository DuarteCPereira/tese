import cv2
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt
import vidProc
import cellSum
import grid_map
import videoRecord



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
    #cap = cv2.VideoCapture('teste_moveprintcore.mp4')
    cap = cv2.VideoCapture(0)
    #cap.set(3, 420)
    #cap.set(4, 380)
    fps_count = 1
    inital_frame = 1
    #length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #last_frame = length-3
    
    

    if cap.isOpened():
        ret, frame = cap.read()
        
        
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()
        #frame = cv2.resize(frame, (1280, 720), fx=0, fy=0, interpolation = cv2.INTER_CUBIC)
        #Make the code only start getting points after intial_frame
        if fps_count % 1 == 0:
            centerPoint = np.array([]).reshape(0, 2)
            midFrame = np.flip(np.asarray(frame.shape[:2])/2)
            intersectionPoints1, cimg, horizontal, vertical, img_bwa = vidProc.findIntPoints(frame, midFrame)
            
            cv2.imshow("linhas horizontais", horizontal)
            cv2.imshow("linhas verticais", vertical)
            cv2.imshow(windowName, cimg)
            
            #vidProc.show_wait_destroy("linhas horizontais", horizontal)
            #vidProc.show_wait_destroy("linhas verticais", vertical)
            #vidProc.show_wait_destroy(windowName, cimg)
            if cv2.waitKey(1) == 27:
                break
        fps_count += 1
        #print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    print(frame.shape)
    #videoRecord.recordVid(10, 'teste_video_record.mp4')
    
    
    

main()
