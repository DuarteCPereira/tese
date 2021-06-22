import numpy as np
import cellSum
from matplotlib import pyplot as plt


def nRowsCols(tg, d_min):
    cols = sorted(tg[:, 0])
    n_cols = 0
    Dx = 0
    for i in range(0,len(cols)-1):
        d = cols[i+1] - cols[i]
        if d > d_min:
            n_cols += 1
            Dx += d
    Dx_mean = Dx / n_cols
    print('o número de colunas é', n_cols, 'com um espaçamento médio de', Dx_mean, '!')

    rows = sorted(tg[:, 1])
    n_rows = 0
    Dy = 0
    for i in range(0,len(rows)-1):
        d = rows[i+1] - rows[i]
        if d > d_min:
            n_rows += 1
            Dy += d
    Dy_mean = Dy / n_rows
    print('o número de linhas é', n_rows, 'com um espaçamento médio de', Dy_mean, '!')
    return n_rows, n_cols


def createMesh(n_rows, n_cols, side_len):

    a = np.linspace(0, n_cols*side_len, n_cols+1)
    b = np.linspace(0, n_rows*side_len, n_rows+1)
    xx, yy = np.meshgrid(a, b)
    #plt.plot(xx, yy, marker='.', color='k', linestyle='none')
    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.set_xticks(a)
    ax.set_yticks(b)
    plt.grid(True, linewidth=0.3, color='#808080', linestyle='-')
    ax.plot(xx, yy, marker='.', color='k', linestyle='None')
    #ax.plot(xx, yy, ls="None", marker=".")

    plt.show()



if __name__ == '__main__':
    frames = {
        0: np.array([[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]),
        }
    a = np.array([[4, 1], [4, 2], [4, 3]])
    #a = np.array([[4, 1]])
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
        totalGrid[i], _, _, D_xy_mean_total = cellSum.continuousGrid(frames[i-1],frames[i],totalGrid[i-1],totalGrid[i-1],framesc[i-1],framesc[i],gridRotation,gridRotation1,D_xy_mean_total)

    #cellSum.plotIntPoints(totalGrid[10], '+b')
    tg = totalGrid[10]
    n_rows, n_cols = nRowsCols(tg, 0.1)
    createMesh(n_rows, n_cols, 20)