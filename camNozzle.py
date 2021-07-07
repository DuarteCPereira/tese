import numpy as np
import vidProc
import videoRecord
import cellSum


def printCalibrationShape():
    #chamar função que permite enviar o GCode que imprime a forma de calibração

    #Subir a Cabeça de impressão
    
    return None

def movePrintCore(displacement_vector):
    #Dar instrução do movimento e Gravar o video correspondente ao movimento
    
    #Gravar video
    videoRecord.recordVid(time, name)

    cap = cv2.VideoCapture(name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame = length
    #last_frame = 295
    fps_count = 1
    inital_frame = 5

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


    #Record 
    
    return d, d_total


def nozzleCamDist(frame, intersectionPoints, p, cel, cel_side):
    #Entra o frame final e encontra-se a coordenada do centro da forma de calibração
    vidProc.findCircles(frame)
    #Obter a célula e as coordenadas onde se encontra o nozzle
    rect_nozzle, cel_nozzle = cellSum.fetchCellPoints(nozzle_cord, intersectionPoints, 10)
    cimg, cel_cord_nozzle = vidProc.four_point_transform(frame, rect_init, nozzle_cord)

    #Vector between center of camera and nozzle
    vec_cels = cel_nozzle - cel
    vec_inside_cel = cel_cord_nozzle - p
    #180 é o numero de pixeis por celula
    vec = np.flip(vec_cels*cel_side) + vec_inside_cel*(cel_side/180)

    return vec

