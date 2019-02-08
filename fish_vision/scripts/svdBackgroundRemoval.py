'''
    Functions to apply regular singular value decomposition to generic stationary video
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

# -- 
# Helpers
def create_data_matrix_from_video(clip, k=5, scale=50): 
    _list = []
    for i in range(k * int(clip.duration)): 
        print(i)
        out = scipy.misc.imresize(rgb2gray(clip.get_frame(i/float(k))).astype(int), scale).flatten()
        _list.append(out)
    return np.vstack(_list).T

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def yeildMatrix(video_path): 
    video = mpe.VideoFileClip(video_path)
    video = video.subclip(0,50)
    video = video.resize(video.size[::-1])
    video = video.resize(0.25)
    scale = 100
    dims = (int(320 * (float(scale)/100)), int(180 * (float(scale)/100)))
    M = create_data_matrix_from_video(video, 100, scale)
    return M


def removeBackground(pixel_matrix, out_file): 
    u, s, v = decomposition.randomized_svd(pixel_matrix, 2)
    d = np.dot(u, np.diag(s))
    low_rank = np.dot(d, v)
    scale = 100
    dims = (int(320 * (float(scale)/100)), int(180 * (float(scale)/100)))
    plt.imsave(fname=out_file, arr=np.reshape(low_rank[:,140], dims), cmap='gray')

def matrixDecompose(video_path): 
    pixel_matrix = yeildMatrix(video_path)
    out_file = video_path.replace(video_path[-4:], '') + '_background.jpg'
    removeBackground(pixel_matrix, out_file)

