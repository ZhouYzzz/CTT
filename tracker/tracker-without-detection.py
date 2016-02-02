#!/usr/bin/env python

import dlib
import cv2
import os, os.path
import time
import numpy as np
import argparse
from readGroundTruth import readGT
from client.assign import overlap

parser = argparse.ArgumentParser(description='Single Tracker')
parser.add_argument('name',type=str,help='Data Base Name')
imdb_name = parser.parse_args().name
print 'Name:', imdb_name


# global varibles
print 'Modules prepared, Demo starts...'
this_file_path = os.path.dirname(os.path.abspath(__file__))
# imdb_name = 'car'
imdb_path = os.path.join(this_file_path, '../vot2014', imdb_name)

print 'IMG path:', imdb_path
assert os.path.exists(imdb_path)
_, _, files = os.walk(imdb_path).next()
img_count = len(files) - 7
print 'IMG count:', img_count

import numpy as np
all_gt = np.loadtxt(imdb_path+'/groundtruth.txt',delimiter=',')
gt = all_gt[0].astype(np.int)
initbox = [gt[2],gt[3],gt[6],gt[7]]
print initbox

GT = readGT(imdb_name)

for idx in xrange(0,img_count):
    # print 'Frame', idx + 1
    img = cv2.imread(imdb_path+'/%08d.jpg'%(idx+1))
    # print img.shape
    assert img != None
    try:
        tracker
    except NameError:
        tracker = dlib.correlation_tracker()
        tracker.start_track(img, dlib.rectangle(*initbox))

    tracker.update(img)

    rect = tracker.get_position()
    box = [int(rect.left()), int(rect.top()),\
            int(rect.right()), int(rect.bottom())]
    print overlap(box,GT[idx])
        
       # pt1 = (int(rect.left()),int(rect.top()))
       # pt2 = (int(rect.right()),int(rect.bottom()))
       # print pt1, pt2
       # cv2.rectangle(img,pt1,pt2,(255,255,255),2)
       # cv2.imshow('Vedio', img)
       # cv2.waitKey(100)


print tracker
