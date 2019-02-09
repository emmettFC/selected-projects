'''
Combined implementation of SVD for 'empty' initialization & Motion detection openCv
    I:   Isolate background of video
    II:  Use background to initialize 'empty' approximation for first frame
    III: Apply openCV motion detection implementation
'''

# --
# Dependancies

import datetime
import imutils
import time
import cv2
import moviepy.editor as mpe
from glob import glob
import sys, os
import numpy as np
import scipy
import matplotlib.pyplot as plt
from sklearn import decomposition 
import argparse
from svdBackgroundRemoval import * 
from buildAnnotation import * 

# -- 
# Command line interface
parser = argparse.ArgumentParser(description='Apply motion detection in openCV')
parser.add_argument('--video', type=str, dest='video', action="store")
args = parser.parse_args()

# --
# Define global variables
_file = args.video
background = _file.replace(_file[-4:], '') + '_background.jpg'

# -- 
# Apply singular value decomposion to produce empty intitialization
matrixDecompose(_file)

# -- 
# Load empty approximation as first frame
firstFrame = cv2.imread(background)
firstFrame = imutils.resize(firstFrame, width=500)
firstFrame = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
firstFrame = cv2.GaussianBlur(firstFrame, (21, 21), 0)


# -- 
# Load video into openCv
camera = cv2.VideoCapture(_file)


# -- 
# Run motion detection with inferred first frame
counterLab = 0
while True:
    (grabbed, frame) = camera.read()
    text = "No Fish Detected"
    if not grabbed:
        break
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 30, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # loop over the contours
    counter = 0
    counterClear = 0
    for c in cnts:
        # if the contour is too small, ignore it (hardcoded min value from arg vector)
        if cv2.contourArea(c) < 500:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        counter += 1
        if cv2.contourArea(c) > 14000:
            counterClear +=1
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Fish Detected"
    if (counter, counterClear) == (1,1): 
        outFile = './foundFrames/frame' + str(counterLab) + '.jpg'
        cv2.imwrite(outFile, frame)
        # build annotation xml file
        buildAnnotation(x, y, h, w, outFile, 'goldfish', 'foundFrames')
        counterLab +=1
        # write out labeled frame
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Tank Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # show the frame and record if the user presses a key
    cv2.imshow("Tank Monitor", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()












