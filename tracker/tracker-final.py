#!/usr/bin/env python

# Tracking related
import dlib, cv2
import numpy as np
# Basic Modules
import os, sys
import argparse
from threading import Thread
from logIO import logCreate
# HTTP related
import requests

# Cloud Server
URL = 'http://yaolaoban.eva0.nics.cc:5000/detect'
# global varibles
this_file_path = os.path.dirname(os.path.abspath(__file__))
imdb_name = 'Jumping'
imdb_path = os.path.join(this_file_path, 'img', imdb_name)
_, _, files = os.walk(imdb_path).next()
img_count = len(files) - 1
i = 1
# IMG, BOX and status
showimg = False
updated = True
updtbox = [0,0,0,0]
oldbox  = [0,0,0,0]
crtbox  = [0,0,0,0]
# Tracker
tracker = dlib.correlation_tracker()

def adjust_box(actbox, oldbox, crtbox):
    '''input:
       1. actbox (Actual Box) : the bbox returned by the server
       2. oldbox (Old Box)    : the bbox of img sent to server
       3. crtbox (Current Box): the bbox now returned by tracker
       output:
       1. newbox (New Box)    : the adjusted bbox
    '''
    newbox = actbox
    newbox[0] += crtbox[0] - oldbox[0]
    newbox[1] += crtbox[1] - oldbox[1]
    newbox[2] += crtbox[2] - oldbox[2]
    newbox[3] += crtbox[3] - oldbox[3]
    return newbox

def showIMG(img, box, time=10):
    cv2.rectangle(img, box[0:1], box[2:3], 
			(255,255,255), 2)
    cv2.imshow('Image', img)
    cv2.waitKey(time)

def encode_box(box):
    '''encode a box (a list of 4 ints) for posting'''
    en_box = {
    	'L'	:	box[0],
    	'U'	:	box[1],
    	'R'	:	box[2],
    	'B'	:	box[3]}
    return en_box

def postIMG():
    global i
    global updated
    global updtbox, oldbox, crtbox
    f = open(imdb_path+'/%04d.jpg'%i)
    r = requests.post(url=URL, 
                data=encode_box(crtbox),
    		files={'img':f})
    updtbox = r.json()['bbox']
    updtbox = adjust_box(updtbox, oldbox, crtbox)
    updated = True
    f.close()
    return

def start_tracking():
    global updated
    global i, img_count
    global updtbox, oldbox, crtbox
    while i <= img_count:
    	# get a new frame
    	img = cv2.imread(imdb_path+'/%04d.jpg'%i)
    	# update the tracker
    	if updated:
	    # tracker.start_track()
    	    tracker.start_track(img, 
		dlib.rectangle(*updtbox))
	    oldbox = updtbox
	    updated = False
	    # post a new frame
	    trd_post = Thread(target=postIMG)
	    trd_post.start()
	else:
	    # tracker.update()
	    tracker.update(img)

	rect = tracker.get_position()
	pt1 = [int(rect.left()), int(rect.top())]
        pt2 = [int(rect.right()),int(rect.bottom())]
        crtbox = pt1 + pt2
        f.write(str(crtbox)+'\n')
        if i%10 == 0:
            print 'frame',i,'returns',crtbox
        if showimg:
            showIMG(img, crtbox, 2000)

        # next frame
        i +=1

def init_firstframe_by_detection():
    pass

def init_firstframe_by_grdtruth():
    global updtbox, oldbox, crtbox
    gtfile = open(imdb_path+'/'+'groundtruth_rect.txt','r')
    line = gtfile.readline()
    points = line[:-1].split(',')
    points = map(int, points)
    points[2] += points[0]
    points[3] += points[1]
    gtfile.close()
    crtbox = points
    updtbox = crtbox
    oldbox = crtbox
    img = cv2.imread(imdb_path+'/0001.jpg')
    tracker.start_track(img, dlib.rectangle(*crtbox))

def parse_args():
    '''Parse input arguments.'''
    parser = argparse.ArgumentParser(description='Terminal')
    parser.add_argument('--local', dest='LOCAL',
        help='run on local server',
        action='store_true')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    if args.LOCAL:
        URL = 'http://0.0.0.0:5000/detect'
    
    print 'Start tracking',imdb_name
    f = logCreate()
    f.write(imdb_name+'final\n')
    init_firstframe_by_grdtruth()
    start_tracking()
    print 'Tracking finished, log file:',f.name
