import numpy as np
import cellSum
from matplotlib import pyplot as plt
import math


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


def createMesh(n_rows, n_cols, side_len, p_init, p_end, cel_init, end_cel):

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

    #plot do ponto inicial
    c = [((cel_init[1]-1)*side_len)+(p_init[0] /180)*(side_len), ((cel_init[0]-1)*side_len)+(p_init[1] /180)*(side_len)]
    ax.plot(c[0], c[1], marker='+', color='g')

    #plot do ponto final
    d = [((end_cel[1]-1)*side_len)+(p_end[0] /180)*(side_len), ((end_cel[0]-1)*side_len)+(p_end[1] /180)*(side_len)]
    ax.plot(d[0], d[1], marker='*', color='g')

    ax.arrow(c[0], c[1], d[0] - c[0], d[1] - c[1], head_width=0.2, head_length=0.2, fc='r', ec='r')

    plt.show()
    return None

def dist_calc(p_init, p, cel_init, cel, cel_side):
    dist_cels = cel - cel_init
    dist_inside_cel = p - p_init
    #mudar este 180 mais tarde
    d = np.flip(dist_cels*cel_side) + dist_inside_cel*(cel_side/180)
    d_total = math.sqrt((d[0]**2) + (d[1]**2))
    return d, d_total

def global_cel_location(coordinate, IP1, n_rows_i, n_cols_i, tg, cel_init, n_rows_tg, n_cols_tg, D_xy_mean_total, d_min, tolerance):
    _, cel = cellSum.fetchCellPoints(coordinate, IP1, tolerance)
    #check where the boundaries are located (left(-1) or right(1), down(-1) or up(1))
    if D_xy_mean_total[0] > 0:
        horizontal_bound = 1
    else:
        horizontal_bound = -1
    if D_xy_mean_total[1] > 0:
        vertical_bound = 1
    else:
        vertical_bound = -1
    
    #check the distance (counted in cells) of the cel where the point is located to the boundaries
    #first know the number of cols and rows that IP1 has
    n_rows, n_cols = nRowsCols(IP1, d_min)
    if vertical_bound == 1:
        d_cells1 = n_rows - cel[0]
        cel_in_tg1 = n_rows_tg - d_cells1
        cel_init1 = cel_init[0]
    elif vertical_bound == -1:
        d_cells1 = cel[0]
        cel_in_tg1 = d_cells1
        cel_init1 = n_rows_tg - (n_rows_i - cel_init[0])

    if horizontal_bound == 1:
        d_cells2 = n_cols - cel[1]
        cel_in_tg2 = n_cols_tg - d_cells2
        cel_init2 = cel_init[1]
    elif horizontal_bound == -1:
        d_cells2 = cel[1]
        cel_in_tg2 = d_cells2
        cel_init2 = n_cols_tg - (n_cols_i - cel_init[1])


    cel_in_tg = [cel_in_tg1, cel_in_tg2]
    start_cel = [cel_init1, cel_init2]
    return start_cel, cel_in_tg

    



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