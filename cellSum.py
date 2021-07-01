import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.spatial import distance

def dsearchn(nodes, node):
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    dist=distance.cdist([node],[nodes[np.argmin(dist_2)]],'euclidean')
    return np.argmin(dist_2),dist


def continuousGrid(intersectionPoints, intersectionPoints1, sumPoints, sumPointsc, centroidPoints, centroidPoints1,
                   gridRotation, gridRotation1, D_xy_mean_total, centerPoint, midFrame):
    gridRotation1 = -gridRotation1
    gridRotation = -gridRotation
    rotMtx1 = [[math.cos(gridRotation1), -math.sin(gridRotation1)], [math.sin(gridRotation1), math.cos(gridRotation1)]]
    rotMtx = [[math.cos(gridRotation), -math.sin(gridRotation)], [math.sin(gridRotation), math.cos(gridRotation)]]
    intersectionPoints = np.matmul(intersectionPoints, rotMtx)
    intersectionPoints1 = np.matmul(intersectionPoints1, rotMtx1)
    rowsCols = intersectionPoints.shape
    rowsCols1 = intersectionPoints1.shape
    rowsColsc = centroidPoints.shape
    rowsColsc1 = centroidPoints1.shape

    K = np.array([]).reshape(0, 1)
    Kc = np.array([]).reshape(0, 1)
    D_xy = np.array([]).reshape(0, 2)
    Dc_xy = np.array([]).reshape(0, 2)
    oldPoints = np.array([]).reshape(0, 2)
    newPoints = np.array([]).reshape(0, 2)
    oldPointsc = np.array([]).reshape(0, 2)
    newPointsc = np.array([]).reshape(0, 2)
    newPointsCorr = np.array([]).reshape(0, 2)
    newPointsCorrc = np.array([]).reshape(0, 2)
    indOld = np.array([]).reshape(0, 1)
    oldPointCounter = 0
    oldPointCounterc = 0

    for i in range(0, rowsCols1[0]):
        k, dist = dsearchn(intersectionPoints, intersectionPoints1[i, :])
        if dist < 110:
            K = np.vstack((K, k))
            indOld = np.vstack((indOld, i))
            d_xy = intersectionPoints[k][:] - intersectionPoints1[i][:]
            D_xy = np.vstack((D_xy, d_xy))
            oldPoints = np.vstack((oldPoints, intersectionPoints[k][:]))
            oldPointCounter += 1

    indOld = np.reshape(indOld, len(indOld))
    vec = np.arange(0, rowsCols1[0])
    vec = np.delete(vec, indOld.astype(int))
    D_xy_mean = np.mean(D_xy, axis=0)
    D_xy_mean_total = D_xy_mean_total + D_xy_mean
    IP1_olds = intersectionPoints1[indOld.astype(int)]
    for j in vec:
        #q é o indice no IP1 do ponto mais próximo ao newPoint
        q, _ = dsearchn(IP1_olds, intersectionPoints1[j])
        #k é o indice no IP do ponto mais proximo ao newPoint
        k, _ = dsearchn(intersectionPoints, intersectionPoints1[j])
        #w é o indice na totalGrid onde o newPoint é mais próximo
        w, _ = dsearchn(sumPoints, IP1_olds[q] + D_xy_mean_total)
        d_corr = IP1_olds[q] - intersectionPoints1[j]
        d_corr1 = sumPoints[w] - intersectionPoints[k]
        #print('totalGridPoint ->',sumPoints[w], 'IP_old ->', intersectionPoints[k], 'IP1_old ->', IP1_olds[q], 'IP1_new ->', intersectionPoints1[j])
        newPoints = np.vstack((newPoints, intersectionPoints1[j]))
        a = sumPoints[w] - d_corr
        newPointsCorr = np.vstack((newPointsCorr, a))
        #newPointsCorr = np.vstack((newPointsCorr, intersectionPoints[k] - d_corr + d_corr1))

    cIP1, _ = dsearchn(intersectionPoints1, midFrame)
    cIP, _ = dsearchn(intersectionPoints, intersectionPoints1[cIP1])
    d = intersectionPoints[cIP] - intersectionPoints1[cIP1]
    centerPointCorr = centerPoint[-1, :] + d
    centerPoint = np.vstack((centerPoint, centerPointCorr))
    #print(newPointsCorr)
    sumPoints = np.vstack((sumPoints, newPointsCorr))
    #print(D_xy_mean_total)
    #plotabc(intersectionPoints, intersectionPoints1, midFrame, '+b', 'xr', '3g')

    return sumPoints, oldPoints, newPoints,  D_xy_mean_total, centerPoint

def fetchCellPoints(coordinate, totalGrid, tolerance):
    sorted_by_cols = totalGrid[totalGrid[:, 0].argsort()]
    sorted_by_rows = totalGrid[totalGrid[:, 1].argsort()]
    
    cols_left_cp_i = np.where(sorted_by_cols[:, 0] < coordinate[0]+tolerance)[0]
    cols_left_cp = sorted_by_cols[cols_left_cp_i]
    sorted_by_row_l = cols_left_cp[cols_left_cp[:, 1].argsort()]
    sorted_by_row_l_i = np.where(sorted_by_row_l[:, 1] < coordinate[1]+tolerance)[0]
    rows_left_cp_b = sorted_by_row_l[sorted_by_row_l_i]

    left_bottom_corner = [cols_left_cp[-1,0], rows_left_cp_b[-1,1]]
    left_top_corner = [cols_left_cp[-1,0], sorted_by_row_l[sorted_by_row_l_i[-1]+1,1]]
    
    print('left bottom corner coordinates:', left_bottom_corner)
    print('left top corner coordinates:', left_top_corner)

    cols_right_cp_i = list(range(cols_left_cp_i[-1], len(totalGrid)))
    cols_right_cp = sorted_by_cols[cols_right_cp_i]
    sorted_by_row_r = cols_right_cp[cols_right_cp[:, 1].argsort()]
    sorted_by_row_r_i = np.where(sorted_by_row_r[:, 1] < coordinate[1]+tolerance)[0]
    rows_right_cp_b = sorted_by_row_r[sorted_by_row_r_i]
    
    right_bottom_corner = [cols_right_cp[1,0], rows_right_cp_b[-1,1]]
    right_top_corner = [cols_right_cp[1,0], sorted_by_row_r[sorted_by_row_r_i[-1]+1,1]]
    
    print('right bottom corner coordinates:', right_bottom_corner)
    print('right top corner coordinates:', right_top_corner)
    

    #Ajustar este parametro "d_min"
    d_min = 70
    cel_col = 0
    # Célula em que se encontra o ponto em questão
    for i in range(0,len(sorted_by_cols)-1):
        d = sorted_by_cols[i+1,0] - sorted_by_cols[i,0]
        if d > d_min:
            cel_col += 1
        if sorted_by_cols[i+1,0] - tolerance > coordinate[0]:
            break
    
    cel_row = 0
    for j in range(0,len(sorted_by_rows)-1):
        d = sorted_by_rows[j+1,1] - sorted_by_rows[j,1]
        if d > d_min:
            cel_row += 1
        if sorted_by_rows[j+1,1] - tolerance > coordinate[1]:
            break

    cel = [cel_row, cel_col]
    rect = np.array([left_top_corner, right_top_corner, right_bottom_corner, left_bottom_corner], dtype=np.float32)

    return rect, cel

def plotIntPoints(totalGrid, marker):
   
    for i in range(0, len(totalGrid)):
        plt.plot(totalGrid[i][0], totalGrid[i][1], marker)
    plt.show()
   #for i in range(0,len(totalGrid)):
    #    plt.plot(totalGrid[i][0],totalGrid[i][1],'+b')
     #   plt.show()

def plotab(a, b, marker_a, marker_b):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    #plt.grid(True, linewidth=0.3, color='#808080', linestyle='-')
    ax.plot(a[:, 0], a[:, 1], marker_a)
    ax.plot(b[:, 0], b[:, 1], marker_b)
    #for i in range(1, len(b)):
        #ax.quiver(b[i, 0], b[i, 1], b[i, 0]-b[i-1, 0], b[i, 1]-b[i-1, 1], color = marker_b, scale=100, scale_units='inches', width = 0.003)

    plt.show()

def plot_a_b(a, b, marker_a, marker_b):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    #plt.grid(True, linewidth=0.3, color='#808080', linestyle='-')
    ax.plot(a[:, 0], a[:, 1], marker_a)
    ax.plot(b[0], b[1], marker_b)
    #for i in range(1, len(b)):
        #ax.quiver(b[i, 0], b[i, 1], b[i, 0]-b[i-1, 0], b[i, 1]-b[i-1, 1], color = marker_b, scale=100, scale_units='inches', width = 0.003)

    plt.show()

def plotabc(a, b, c, marker_a, marker_b, marker_c):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(a[:, 0], a[:, 1], marker_a)
    ax.plot(b[:, 0], b[:, 1], marker_b)
    ax.plot(c[0], c[1], marker_c)
    plt.show()

if __name__ == '__main__':
    
    frames = {
        0: np.array([[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]),
    }
    #a = np.array([[4, 1], [4, 2], [4, 3]])
    a = np.array([[4, 1]])
    frames[1] = np.subtract(np.concatenate((frames[0], a), axis=0), [0.1, 0.1])
    for i in range(2, 10):
        frames[i] = np.subtract(frames[i - 1], [0.1, 0.1])
    frames[10] = np.concatenate((frames[9], [[4.1, 0.1], [4.1, 1.1], [4.1, 2.1]]))
    gridRotation = 0
    gridRotation1 = 0
    totalGrid = {0: frames[0]}
    D_xy_mean_total = [0, 0]

    framesc = {
        0: np.array([[1.5, 1.5], [2.5, 1.5], [1.5, 2.5], [2.5, 2.5]]),
    }
    b = np.array([[3.5, 1.5], [3.5, 2.5]])
    framesc[0] = np.subtract(np.concatenate((framesc[0], b), axis=0), [0.1, 0.1])
    for i in range(1, 10):
        framesc[i] = np.subtract(framesc[i - 1], [0.1, 0.1])
    framesc[10] = np.concatenate((framesc[9], [[3.6, 0.6], [3.6, 1.6]]))
    totalGridc = {0: framesc[0]}
    
    for i in range(1,len(frames)):
        totalGrid[i], _, _, D_xy_mean_total=continuousGrid(frames[i-1],frames[i],totalGrid[i-1],totalGrid[i-1],framesc[i-1],framesc[i],gridRotation,gridRotation1,D_xy_mean_total)


    for i in range(0,len(totalGrid[list(totalGrid.keys())[-1]])):
        plt.plot(totalGrid[list(totalGrid.keys())[-1]][i][0],totalGrid[list(totalGrid.keys())[-1]][i][1],'+b')
    plt.show()
