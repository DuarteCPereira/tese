import cv2
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt
import vidProc
import calibrateFisheye
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
    cap = cv2.VideoCapture('video_grid_new_cam1.h264')
    fps_count = 1
    inital_frame = 100
    last_frame = 400
    #cap.set(3, 1024)
    #cap.set(4, 576)
    

    if cap.isOpened():
        ret, frame = cap.read()
        
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()

        #Make the code only start getting points after intial_frame
        if fps_count >= inital_frame and fps_count <= last_frame and fps_count % 5 == 0:

            #find points of the first frame
            if fps_count == inital_frame:
                centerPoint = np.array([]).reshape(0, 2)
                midFrame = np.flip(np.asarray(frame.shape[:2])/2)
                centerPoint = np.vstack((centerPoint, midFrame))
                print(centerPoint[-1,:])
                intersectionPoints, totalGrid, img = vidProc.findInitPoints(frame, midFrame)
                D_xy_mean_total = [0, 0]
                rect_init, cel_init = cellSum.fetchCellPoints(midFrame, intersectionPoints)
                cimg, cel_cord_init = vidProc.four_point_transform(img, rect_init, midFrame)
                vidProc.show_wait_destroy('teste', cimg)
            

            #cimg = calibrateFisheye.undist(frame,Kd,Dd)
            #lines,cimg=vidProc.binaryGridDetection(frame)
            #vidProc.show_wait_destroy('posição do centro na celula',cimg)
            intersectionPoints1, cimg, horizontal, vertical, img_bwa = vidProc.findIntPoints(frame, midFrame)
            totalGrid, oldPoints, newPoints, D_xy_mean_total, centerPoint, cel, rect = cellSum.continuousGrid(intersectionPoints, np.asarray(intersectionPoints1), totalGrid,totalGrid, intersectionPoints,np.asarray(intersectionPoints1),0,0,D_xy_mean_total, centerPoint, midFrame)
            #print(centerPoint[-1,:])
            #make the mew frame the old for the next iteration of cycle
            intersectionPoints = np.asarray(intersectionPoints1)

            #cimg = vidProc.findCircles(frame)
            rect, cel = cellSum.fetchCellPoints(midFrame, intersectionPoints)
            cimg1, p_after = vidProc.four_point_transform(cimg, rect, midFrame)
            cv2.imshow(windowName, cimg)
            #vidProc.show_wait_destroy(windowName, cimg1)
            #cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
            #cv2.imshow("frame", cimg)
            #cv2.imshow("horizontal", horizontal)
            #cv2.imshow("vertical", vertical)
            #cv2.imshow("img_bwa", img_bwa)
            
            if cv2.waitKey(1) == 27:
                break
        fps_count += 1
        #print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
    n_rows, n_cols = grid_map.nRowsCols(totalGrid, 70)
    grid_map.createMesh(n_rows, n_cols, 20)
    _, cel = cellSum.fetchCellPoints(centerPoint[-1], totalGrid)
    d = grid_map.dist_calc(np.asarray(p_after), np.asarray(cel_cord_init), np.asarray(cel_init), np.asarray(cel), 20)
    print(d)

    
main()
