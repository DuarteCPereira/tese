import cv2
import numpy as np
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt
import cellSum
from operator import itemgetter



def undist(img,data_dict):
    cameraM=np.array(data_dict['camera_M'])
    dist=np.array(data_dict['dist_coeff'])
    h,  w = img.shape[:2]
    newCameraM, roi = cv2.getOptimalNewCameraM(cameraM, dist, (w,h), 1, (w,h))
    x, y, w, h = roi
    dst = cv2.undistort(img, cameraM, dist, None, newCameraM)
    dst = dst[y:y+h, x:x+w]
    return dst

def show_wait_destroy(winname, img):
    cv2.imshow(winname, img)
    cv2.moveWindow(winname, 500, 0)
    cv2.waitKey(0)
    cv2.destroyWindow(winname)

def binaryGridDetection(raw_frame):
    #Find image center
    centerPoint = np.asarray(raw_frame.shape[0:2])/2
    #Grid intersection detection
    frame_gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    ret,binary = cv2.threshold(frame_gray,70,255,cv2.THRESH_BINARY_INV)
     
    edges = cv2.Canny(frame_gray,80,80)
    cdst = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR)
    lines = cv2.HoughLines(edges, 0.5, np.pi / 360, 120, None, 0, 0)
    # Draw the lines
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
    
    #show_wait_destroy("Source", raw_frame)
    #show_wait_destroy("Detected Lines (in red) - Standard Hough Line Transform", cdst) 
    
    return lines,cdst

def finddirs(lines):
    a=0
    b=[]
    c=[]
    for i in range(0, len(lines)):
        if (math.degrees(lines[i][0][1])%360)>-45 and (math.degrees(lines[i][0][1])%360)<45:
            b.append(math.degrees(lines[i][0][1])%360)
        if (math.degrees(lines[i][0][1])%360)>135 and (math.degrees(lines[i][0][1])%225)<225:
            b.append((math.degrees(lines[i][0][1])%360)-180)
        if (math.degrees(lines[i][0][1])%360)>45 and (math.degrees(lines[i][0][1])%225)<135:
            c.append(math.degrees(lines[i][0][1])%360)
        a+=1
    dir1=np.mean(b)
    dir2=np.mean(c)
    return dir1,dir2  


def findIntPoints(img1, midFrame):
    _,binary = cv2.threshold(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY),70,200,cv2.THRESH_BINARY_INV)
    img = np.copy(img1)
    #show_wait_destroy("Image", binary)
    # Create the images that will use to extract the horizontal and vertical lines
    horizontal = np.copy(binary)
    vertical = np.copy(binary)

    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    horizontal_size = cols // 10

    # Specify size on vertical axis
    rows = vertical.shape[0]
    verticalsize = rows // 10

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)
    img_bwa = cv2.bitwise_and(vertical,horizontal)
    #horizontal = cv2.dilate(horizontal, horizontalStructure)
    # Show extracted horizontal lines
    #show_wait_destroy("horizontal", horizontal)
    #show_wait_destroy("horizontal", vertical)
    #show_wait_destroy("horizontal", img_bwa)
    #find centroids of blobs
    # find contours in the binary image
    contours, hierarchy = cv2.findContours(img_bwa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    intersectionPoints=[]
    cv2.rectangle(img, (200, 50), (cols-200, rows-50), (0, 255, 20), 2)
    drawCenter(img, midFrame)
    for c in contours:
        if cv2.contourArea(c)>80:
            # calculate moments for each contour
            M = cv2.moments(c)
            if M["m00"] != 0:
                # calculate x,y coordinate of center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                if cX < cols - 200 and cX > 200 and cY < rows - 100 and cY > 100:
                    intersectionPoints.append([cX,cY])
                    cv2.circle(img, (cX, cY), 3, (0, 0, 255), -1)
                    cv2.circle(img_bwa, (cX, cY), 3, (0, 0, 255), -1)
                    #cv2.putText(img_bwa, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # display the image
    #show_wait_destroy('img_bwa', img_bwa)
    return intersectionPoints,img, horizontal, vertical, img_bwa

def findInitPoints(img1, midFrame):
    intersectionPoints, img, _, _, _ = findIntPoints(img1, midFrame)
    totalGrid = intersectionPoints
    return np.asarray(intersectionPoints), np.asarray(totalGrid), img

def findCircles(img):
    cimg=np.copy(img)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #define range of bluevcolor in hsv
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    show_wait_destroy('123', mask)
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT,1.5,20, param1=90,param2=20,minRadius=20,maxRadius=50)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
    
    return(cimg, i[:2])

def four_point_transform(image, rect, midFrame):
    # obtain a consistent order of the points and unpack them
    # individually
    #first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left

    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    #
    maxHeight = 180
    maxWidth = 180
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform Mx and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    '''
    Transformação retirada de 
    https://stackoverflow.com/questions/57399915/how-do-i-determine-the-locations-of-the-points-after-perspective-transform-in-t
    '''
    # Here you can transform your point
    p = midFrame
    px = (M[0][0]*p[0] + M[0][1]*p[1] + M[0][2]) / ((M[2][0]*p[0] + M[2][1]*p[1] + M[2][2]))
    py = (M[1][0]*p[0] + M[1][1]*p[1] + M[1][2]) / ((M[2][0]*p[0] + M[2][1]*p[1] + M[2][2]))
    p_after = (int(px), 180-int(py))
    # return the warped image
    return warped, p_after

def drawCenter(image, center_coordinates):
    radius = 20
    #color in BGR
    color = (255, 0, 0)
    # Line thickness of -1 px (-1 fills the circle)
    thickness = -1

    #coordinates correspond to the center of the image
    center_coordinates = center_coordinates.astype(int)
    image = cv2.circle(image, center_coordinates, radius, color, thickness)
    return image


def rescaleFrame(frame, scale):
	width = int(frame.shape[1] * scale)
	height = int(frame.shape[0] * scale)

	dimensions = (width, height)

	return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def cropImage(img, x, w, y, h):
    return img[y:y+h, x:x+h]
