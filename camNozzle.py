import numpy as np
import vidProc
import cellSum
import grid_map
import videoRecord
import math
import cv2



def printCalibrationShape():
    #chamar função que permite enviar o GCode que imprime a forma de calibração

    #Subir a Cabeça de impressão
    
    return None

def movePrintCore(time, name, celLen):
    #Dar instrução do movimento e Gravar o video correspondente ao movimento
    
    #Gravar video
    videoRecord.recordVid(time, name)

    cap = cv2.VideoCapture(name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame = length-3
    #print(last_frame)
    #last_frame = 295
    fps_count = 1
    inital_frame = 5

    if cap.isOpened():
        ret, frame = cap.read()
        cols = frame.shape[1]
        
    else:
        ret = False


    while ret:
    
        ret, frame = cap.read()
        

        #Make the code only start getting points after intial_frame
        if fps_count >= inital_frame and fps_count <= last_frame and fps_count % 1 == 0:

            #find points of the first frame
            if fps_count == inital_frame:
                centerPoint = np.array([]).reshape(0, 2)
                midFrame = np.flip(np.asarray(frame.shape[:2])/2)
                centerPoint = np.vstack((centerPoint, midFrame))
                #print(centerPoint[-1,:])
                intersectionPoints, totalGrid, img = vidProc.findInitPoints(frame, midFrame)
                n_rows_i, n_cols_i = grid_map.nRowsCols(intersectionPoints, cols*0.036)
                D_xy_mean_total = [0, 0]
                rect_init, cel_init, sidePx = cellSum.fetchCellPoints(midFrame, intersectionPoints, cols*0.005, cols*0.036)
                cimg, cel_cord_init = vidProc.four_point_transform(img, rect_init, midFrame)
                #print(cel_cord_init)
                #vidProc.show_wait_destroy('teste', cimg)
                #vidProc.show_wait_destroy('teste', img)
                #cellSum.plot_a_b(intersectionPoints, midFrame, '+b', 'xr')
            
            #lines,cimg=vidProc.binaryGridDetection(frame)
            #vidProc.show_wait_destroy('posição do centro na celula',cimg)
            intersectionPoints1, cimg, horizontal, vertical, img_bwa = vidProc.findIntPoints(frame, midFrame)

            if len(intersectionPoints1) < len(intersectionPoints)-5:
                print('frame bugado')
            else:
                totalGrid, oldPoints, newPoints, D_xy_mean_total, centerPoint = cellSum.continuousGrid(intersectionPoints, np.asarray(intersectionPoints1), totalGrid,totalGrid, intersectionPoints,np.asarray(intersectionPoints1),0,0,D_xy_mean_total, centerPoint, midFrame, cols*0.036)
                #make the mew frame the old for the next iteration of cycle
                intersectionPoints = np.asarray(intersectionPoints1)

            #cimg = vidProc.findCircles(frame)

            #vidProc.show_wait_destroy("frame", cimg)

            #Descomentar caso seja para ver a imagem
            #cv2.imshow('preview', cimg)

            #cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
            
            if fps_count == last_frame:
                #vidProc.show_wait_destroy("last Frame", cimg)
                #cellSum.plot_a_b(intersectionPoints, midFrame, '+b', 'xr')
                last_frame_img = frame
            if cv2.waitKey(1) == 27:
                break
            #print(fps_count)
        fps_count += 1
        #print(fps_count)
    cv2.destroyAllWindows()
    cap.release()
    #cellSum.plotab(totalGrid, centerPoint, '+b', 'xr')
    n_rows_tg, n_cols_tg = grid_map.nRowsCols(totalGrid, cols*0.036)
    
    #MUDAR CENTERPOINT PARA PONTO REAL E NAO APROXIMAÇÃO
    rect, cel_last_frame, _ = cellSum.fetchCellPoints(midFrame, intersectionPoints, cols*0.005, cols*0.036)
    cimg1, p_after = vidProc.four_point_transform(cimg, rect, midFrame)
    #print(p_after)
    #vidProc.show_wait_destroy("last frame cell", cimg1)
    
    start_cel, end_cel = grid_map.global_cel_location(midFrame, intersectionPoints, n_rows_i, n_cols_i, totalGrid, cel_init, n_rows_tg, n_cols_tg, D_xy_mean_total, cols*0.036, cols*0.005)
    
    #Descomentar caso seja para dar display da figura com o plot do deslocamento
    #grid_map.createMesh(n_rows_tg, n_cols_tg, 2,np.asarray(cel_cord_init), np.asarray(p_after), np.asarray(start_cel), np.asarray(end_cel))
    d, d_total = grid_map.dist_calc(np.asarray(cel_cord_init), np.asarray(p_after), np.asarray(start_cel), np.asarray(end_cel), celLen)
    print('A distância percorrida foi de', d[0],'[mm] em xx, e', d[1], '[mm] em yy')
    print('A distância total é de ', d_total, '[mm].')


    #Record 
    
    return d, d_total, last_frame_img, intersectionPoints, p_after, cel_last_frame, sidePx


def nozzleCenterDist1(frame, intersectionPoints, p, cel, cel_side):
    #Entra o frame final e encontra-se a coordenada do centro da forma de calibração
    

    cimg, nozzle_cord = vidProc.findCircles(frame)
    #Obter a célula e as coordenadas onde se encontra o nozzle
    rect_nozzle, cel_nozzle, sidePx = cellSum.fetchCellPoints(nozzle_cord, intersectionPoints, frame.shape[1]*0.005, frame.shape[1]*0.036)
    cimg, cel_cord_nozzle = vidProc.four_point_transform(frame, rect_nozzle, nozzle_cord)

    #Vector between center of camera and nozzle
    vec_cels = cel_nozzle - cel
    vec_inside_cel = cel_cord_nozzle - p
    #180 é o numero de pixeis por celula
    vec = np.flip(vec_cels*cel_side) + vec_inside_cel*(cel_side/180)

    return vec


def nozzleCamDistCalc(vec, d):
    vec_nozzle_cam = d + vec
    return vec_nozzle_cam

def nozzleCamProc(celLen):

    d, d_total, last_frame_img, intersectionPoints, p, cel, _ = movePrintCore(10, 'teste_nozzleCamProc.mp4', celLen)

    vec = nozzleCenterDist(last_frame_img, intersectionPoints, np.asarray(p), np.asarray(cel), 2.381)

    vec_nozzle_cam = nozzleCamDistCalc(vec, d)
    print('O vetor entre o nozzle e a camera é de', vec_nozzle_cam)

    return vec_nozzle_cam


def nozzleCenterDist2(frame, midFrame):
    cimg, nozzle_cord = vidProc.findCircles(frame)

    vec = nozzle_cord - midFrame

    return vec

def nozzleCamProc2():
    #Give instruction to print calibration shape

    #Give instruction to raise head

    #Give instruction of first guess of displacement (disp_vector)

    #Get the difference between center of camera and nozzle
    vec = nozzleCenterDist2(frame, midFrame)
    while vec > d_max:
        #Estimate the adjustment displacement (disp_adjust)

        # Give new comand to move (disp_adjust)

        #Update disp_vector
        disp_vector += disp_adjust

        #Get new difference between center of camera and nozzle
        vec = nozzleCenterDist2(frame, midFrame)

    return disp_vector


def MmToPx(dx_1mm, dy_1mm, sidePx, celLen):
    #Give command to move 1mm_xx
    PxPerMm = [sidePx[0]/celLen, sidePx[1]/celLen]

    #Quantity of pixels (in x and y direction) per mm
    dpx_1mm_xx = [int(dx_1mm[0]*PxPerMm[0]), int(dx_1mm[1]*PxPerMm[1])]

    dpx_1mm_yy = [int(dy_1mm[0]*PxPerMm[0]), int(dy_1mm[1]*PxPerMm[1])]

    dpx_mm = np.array([dpx_1mm_xx, dpx_1mm_yy])
    dpx_mm = dpx_mm.transpose()

    return dpx_mm



def steps_mm_cal_xx(A, time, name, celLen):
    #beforing calling this function, M503 and M83 must be sent to printer
    #Get A parameter from M503

    #Give instruction to move 10 mm in xx and get dx
    #_, dx, _, _, _, _ = movePrintCore(time, name)
    
    #dx = 9.9
    
    #Make the printer move 10 mm in x again
    _, dx, _, _, _, _, _ = movePrintCore(time, name, celLen)

    dif = dx - 10
    if abs(dif) < 0.05:
        D = A
        print("Steps are calibrated")

    elif dif != 0:
        D = 10*A/dx
        print("Y_Steps require calibration")

    print(D)

    return D
    
def steps_mm_cal_yy(A, time, name, celLen):
    #beforing calling this function, M503 and M83 must be sent to printer
    #Get A parameter from M503

    #Give instruction to move 10 mm in xx and get dx
    #_, dx, _, _, _, _ = movePrintCore(time, name)
    
    #dx = 9.9
    
    #Make the printer move 10 mm in x again
    _, dy, _, _, _, _, _ = movePrintCore(time, name, celLen)

    dif = dy - 10
    if abs(dif) < 0.05:
        D = A
        print("Steps are calibrated")

    elif dif != 0:
        D = 10*A/dy
        print("Y_Steps require calibration")

    print(D)
    return D

def getSkewCoefxy(dx, dy):
    #move the printCore (-10, 0) for example
    #dx, dx_total = movePrintCore([-10, 0])
    #dx = np.array([-10, 0])
    #move the printCore (0, -10) for example
    #dy, dy_total = movePrintCore([0, -10])
    #dy = np.array([0, -10])

    unit_vector_1 = dx / np.linalg.norm(dx)
    unit_vector_2 = dy / np.linalg.norm(dy)

    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)*(180/math.pi)


    #dot_product = np.dot(dy, dx)
    #angle = (np.arccos(dot_product))*(180/math.pi)
    #xytan = math.tan((math.pi/2)-angle)
    return angle, unit_vector_1, unit_vector_2

#d, _, _, _, _, _, _ = movePrintCore(20, 'test_RP2.mp4', 1.985)
#nozzleCamProc()
