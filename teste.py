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
    cap = cv2.VideoCapture('10mm_100mm_min_xx.mp4')
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame = length
    #last_frame = 295
    fps_count = 1
    inital_frame = 5
    #cap.set(3, 1024)
    #cap.set(4, 576)
    

    if cap.isOpened():
        ret, frame = cap.read()
        
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()

        #Make the code only start getting points after intial_frame
        if fps_count >= inital_frame and fps_count < last_frame and fps_count % 1 == 0:

            #find points of the first frame
            if fps_count == inital_frame:
                centerPoint = np.array([]).reshape(0, 2)
                midFrame = np.flip(np.asarray(frame.shape[:2])/2)
                centerPoint = np.vstack((centerPoint, midFrame))
                print(centerPoint[-1,:])
                intersectionPoints, totalGrid, img = vidProc.findInitPoints(frame, midFrame)
                n_rows_i, n_cols_i = grid_map.nRowsCols(intersectionPoints, 70)
                D_xy_mean_total = [0, 0]
                rect_init, cel_init = cellSum.fetchCellPoints(midFrame, intersectionPoints, 10)
                cimg, cel_cord_init = vidProc.four_point_transform(img, rect_init, midFrame)
                print(cel_cord_init)
                vidProc.show_wait_destroy('teste', cimg)
                vidProc.show_wait_destroy('teste', img)
                cellSum.plot_a_b(intersectionPoints, midFrame, '+b', 'xr')
            
            #lines,cimg=vidProc.binaryGridDetection(frame)
            #vidProc.show_wait_destroy('posição do centro na celula',cimg)
            intersectionPoints1, cimg, horizontal, vertical, img_bwa = vidProc.findIntPoints(frame, midFrame)

            if len(intersectionPoints1) < len(intersectionPoints)-5:
                print('frame bugado')
            else:
                totalGrid, oldPoints, newPoints, D_xy_mean_total, centerPoint = cellSum.continuousGrid(intersectionPoints, np.asarray(intersectionPoints1), totalGrid,totalGrid, intersectionPoints,np.asarray(intersectionPoints1),0,0,D_xy_mean_total, centerPoint, midFrame)
                #make the mew frame the old for the next iteration of cycle
                intersectionPoints = np.asarray(intersectionPoints1)

            #cimg = vidProc.findCircles(frame)
            
            #vidProc.show_wait_destroy("frame", cimg)
            cv2.imshow(windowName, cimg)
            #cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
            
            if fps_count == last_frame:
                vidProc.show_wait_destroy("last Frame", cimg)
                cellSum.plot_a_b(intersectionPoints, midFrame, '+b', 'xr')
            if cv2.waitKey(1) == 27:
                break
        fps_count += 1
        #print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
    n_rows_tg, n_cols_tg = grid_map.nRowsCols(totalGrid, 70)
    
    #MUDAR CENTERPOINT PARA PONTO REAL E NAO APROXIMAÇÃO
    rect, _ = cellSum.fetchCellPoints(midFrame, intersectionPoints, 10)
    cimg1, p_after = vidProc.four_point_transform(cimg, rect, midFrame)
    print(p_after)
    vidProc.show_wait_destroy("last frame cell", cimg1)
    
    start_cel, end_cel = grid_map.global_cel_location(midFrame, intersectionPoints, n_rows_i, n_cols_i, totalGrid, cel_init, n_rows_tg, n_cols_tg, D_xy_mean_total, 70, 10)
    
    grid_map.createMesh(n_rows_tg, n_cols_tg, 2,np.asarray(cel_cord_init), np.asarray(p_after), np.asarray(start_cel), np.asarray(end_cel))
    d, d_total = grid_map.dist_calc(np.asarray(cel_cord_init), np.asarray(p_after), np.asarray(start_cel), np.asarray(end_cel), 2.381)
    print('A distância percorrida foi de', d[0],'[mm] em xx, e', d[1], '[mm] em yy')
    print('A distância total é de ', d_total, '[mm].')

main()
