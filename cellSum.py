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
                   gridRotation, gridRotation1, D_xy_mean_total):
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
    d_xy = 0

    for i in range(0, rowsCols1[0]):
        k, dist = dsearchn(intersectionPoints, intersectionPoints1[i, :])
        if dist < 113:
            K = np.vstack((K, k))
            indOld = np.vstack((indOld, i))
            d_xy = intersectionPoints[k][:] - intersectionPoints1[i][:]
            D_xy = np.vstack((D_xy, d_xy))
            oldPoints = np.vstack((oldPoints, intersectionPoints[k][:]))
            oldPointCounter += 1

    indOld = np.reshape(indOld, len(indOld))
    vec = np.arange(0, rowsCols1[0])
    vec = np.delete(vec, indOld.astype(int))
    print(vec)
    for j in vec:
        q, _ = dsearchn(intersectionPoints1[indOld.astype(int)], intersectionPoints1[j])
        k, _ = dsearchn(intersectionPoints, intersectionPoints1[j])
        w, _ = dsearchn(sumPoints, intersectionPoints1[j] + D_xy_mean_total)
        d_corr = intersectionPoints1[q] - intersectionPoints1[j]
        d_corr1 = sumPoints[w] - intersectionPoints[k]
        newPoints = np.vstack((newPoints, intersectionPoints1[k]))
        newPointsCorr = np.vstack((newPointsCorr, intersectionPoints[k] - d_corr + d_corr1))

    sumPoints = np.vstack((sumPoints, newPointsCorr))
    D_xy_mean = np.mean(D_xy, axis=0)
    D_xy_mean_total = D_xy_mean_total + D_xy_mean

    return sumPoints, sumPointsc, D_xy_mean_total



if __name__ == '__main__':
    
    frames = {
        0: np.array([[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]),
    }
    a = np.array([[4, 1], [4, 2], [4, 3]])
    frames[1] = np.subtract(np.concatenate((frames[0], a), axis=0), [0.1, 0.1])
    for i in range(2, 10):
        frames[i] = np.subtract(frames[i - 1], [0.1, 0.1])
    frames[10] = np.concatenate((frames[9], [[4.1, 0.1], [4.1, 1.1], [4.1, 2.1]]))
    gridRotation = 0
    gridRotation1 = 0
    totalGrid = {0: frames[0]}
    D_xy_mean_total = 0

    framesc = {
        0: np.array([[1.5, 1.5], [2.5, 1.5], [1.5, 2.5], [2.5, 2.5]]),
    }
    b = np.array([[3.5, 1.5], [3.5, 2.5]])
    framesc[0] = np.subtract(np.concatenate((framesc[0], b), axis=0), [0.1, 0.1])
    for i in range(1, 10):
        framesc[i] = np.subtract(framesc[i - 1], [0.1, 0.1])
    framesc[10] = np.concatenate((framesc[9], [[3.6, 0.6], [3.6, 1.6]]))
    totalGridc = {0: framesc[0]}
    #%%
    for i in range(1,len(frames)):
        totalGrid[i], totalGridc[i], D_xy_mean_total=continuousGrid(frames[i-1],frames[i],totalGrid[i-1],totalGridc[i-1],framesc[i-1],framesc[i],gridRotation,gridRotation1,D_xy_mean_total)


    for i in range(0,len(totalGrid[list(totalGrid.keys())[-1]])):
        plt.plot(totalGrid[list(totalGrid.keys())[-1]][i][0],totalGrid[list(totalGrid.keys())[-1]][i][1],'+b')
    plt.show()
