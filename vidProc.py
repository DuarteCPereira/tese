import cv2
import numpy as np
import yaml
import numpy as np
import math
from matplotlib import pyplot as plt


def undist(img,data_dict):
    cameraMatrix=np.array(data_dict['camera_matrix'])
    dist=np.array(data_dict['dist_coeff'])
    h,  w = img.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
    x, y, w, h = roi
    dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMatrix)
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


def findIntPoints(img1):
    _,binary = cv2.threshold(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY),90,250,cv2.THRESH_BINARY_INV)
    img = np.copy(img1)
    # Create the images that will use to extract the horizontal and vertical lines
    horizontal = np.copy(binary)
    vertical = np.copy(binary)

    # Specify size on horizontal axis
    cols = horizontal.shape[1]
    horizontal_size = cols // 30

    # Specify size on vertical axis
    rows = vertical.shape[0]
    verticalsize = rows // 20

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    vertical = cv2.erode(vertical, verticalStructure)
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
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)
        if M["m00"] != 0:
            # calculate x,y coordinate of center
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            intersectionPoints.append([cX,cY])
            cv2.circle(img, (cX, cY), 3, (0, 0, 255), -1)
            cv2.putText(img_bwa, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    # display the image
    #show_wait_destroy("Image", img)

    return intersectionPoints,img

def findInitPoints(img1):
    intersectionPoints, _ = findIntPoints(img1)
    totalGrid = intersectionPoints
    return np.asarray(intersectionPoints), np.asarray(totalGrid)

def findCircles(img):
    cimg=np.copy(img)
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(img_gray,cv2.HOUGH_GRADIENT,1.2,50, param1=100,param2=30,minRadius=10,maxRadius=20)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
    return(cimg)

def rescaleFrame(frame, scale):
	width = int(frame.shape[1] * scale)
	height = int(frame.shape[0] * scale)

	dimensions = (width, height)

	return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)