#!/usr/bin/env python

import _init_paths
# Faster R-CNN
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
# Basic Modules
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2
import argparse
from utils.timer import Timer
# Cloud Server related
from flask import Flask, jsonify, request

# --------------------------------------------------
# 	Global Varibles
# --------------------------------------------------

# Cloud Server Config
# HOST = '0.0.0.0'
HOST = 'yaolaoban.eva0.nics.cc'
PORT = 5000
DEBUG = False
# Detection Config
CONF_THRESH = 0.8
NMS_THRESH = 0.3

# Global Path
this_file_path = os.path.dirname(os.path.abspath(__file__))
imdb_name = 'bolt'
imdb_path = os.path.join(this_file_path, 'img', imdb_name)
log_path = os.path.join(this_file_path, 'logfile/')
tmp_path = os.path.join(this_file_path, 'tmp/')
# Net Model related
CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')

NETS = {'vgg16': ('VGG16',
                  'VGG16_faster_rcnn_final.caffemodel'),
        'zf': ('ZF',
                  'ZF_faster_rcnn_final.caffemodel')}

# --------------------------------------------------
# 	Detection Related
# --------------------------------------------------

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--local', dest='LOCAL',
        help='run a local server',
        action='store_true')
    parser.add_argument('--nms', dest='NMS_THRESH_ENABLE',
        help='enable nms wrapper',
        action='store_true')
    parser.add_argument('--gpu', dest='gpu_id', 
            help='GPU device id to use [0]', default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
            help='Use CPU mode (overrides --gpu)', 
            action='store_true')
    parser.add_argument('--net', dest='demo_net', 
            help='Network to use [vgg16]',
            choices=NETS.keys(), default='vgg16')

    args = parser.parse_args()

    return args

def build_net():
    prototxt = os.path.join(cfg.ROOT_DIR, 'models', 
            NETS[args.demo_net][0], 'faster_rcnn_alt_opt', 
            'faster_rcnn_test.pt')
    caffemodel = os.path.join(cfg.ROOT_DIR, 'data', 
            'faster_rcnn_models', NETS[args.demo_net][1])
    caffe.set_mode_gpu()
    caffe.set_device(args.gpu_id)
    cfg.GPU_ID = args.gpu_id
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)
    return net

def significance(confidence, box1, box2):
    ary1 = np.array(box1)
    ary2 = np.array(box2)
    error = np.linalg.norm(ary1 - ary2, ord = 2)
    sig = confidence / error
    return sig

def detection(img, box, net):
    '''run detection'''
    global CONF_THRESH, NMS_THRESH
    # cls and index : we choose person only
    cls_ind = 14 + 1
    cls = 'person'
    # run detection
    scores, boxes = im_detect(net, img)
    cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
    cls_scores = scores[:, cls_ind]
    dets = np.hstack((cls_boxes,
        cls_scores[:, np.newaxis])).astype(np.float32)
    keep = nms(dets, NMS_THRESH)
    dets = dets[keep, :]
    inds = np.where(dets[:, -1] >= CONF_THRESH)[0]
    num_box = len(inds)
    
    if num_box == 0:
    	print 'No person detected'
    	bbox = box
    	return bbox

    index = 0
    bbox = dets[0, :4]
    confidence = dets[0, 4]
    sig = significance(confidence, bbox, box)
    if num_box > 1:
    	for i in range(1, num_box-1):
    	    tmp_confidence = dets[i, 4]
    	    tmp_bbox = dets[i, :4]
    	    tmp_sig = significance(tmp_confidence, tmp_bbox, box)
    	    if tmp_sig > sig:
    	        sig = tmp_sig
    	        index = i
    	        bbox = dets[index, :4]
    
    bbox = [bbox[0],bbox[1],bbox[2],bbox[3]]
    bbox = map(int,bbox)
    return bbox

def correlation(box, dets):
    num = dets.shape[0]
    # print num
    ipt = 0
    index = 0
    dist = 0
    for i in xrange(num):
        tp_dist = np.linalg.norm(dets[i,0:4]-np.array(box),ord=1)
        tp_ipt = 10/tp_dist
        if tp_ipt > ipt:
            index = i
            ipt = tp_ipt
            dist = tp_dist

    bbox = dets[index,0:4]

    print ipt, dist
    if dist > 100:
        print 'No nearby target matches!'
        return None
    
    if dets[index,-1] < 0.01:
        print 'Not Likely!'
        return None

    bbox = bbox.tolist()
    bbox = map(int,bbox)
    return bbox

def co_detection(img, box, net):
    '''run co_detection'''
    global CONF_THRESH, NMS_THRESH
    # cls and index : we choose person only
    cls_ind = 14 + 1
    cls = 'person'
    # run detection
    scores, boxes = im_detect(net, img)
    cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
    cls_scores = scores[:, cls_ind]
    dets = np.hstack((cls_boxes,
        cls_scores[:, np.newaxis])).astype(np.float32)

    inds = np.where(dets[:,-1]>=0.0001)[0]
    dets = dets[inds,:]
    bbox = correlation(box, dets)
    return bbox


def full_detection(img, box, net):
    '''run full detection'''
    global CONF_THRESH, NMS_THRESH
    scores, boxes = im_detect(net, img)
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        if NMS_THRESH_ENABLE:
            keep = nms(dets, NMS_THRESH)
            dets = dets[keep, :]

    print dets.shape            
    return dets

def decode_box(en_box):
    '''decode posted box to a list of 4 ints'''
    de_box = [	int(en_box['L']),
	    	int(en_box['U']),
	    	int(en_box['R']),
		int(en_box['B'])]	
    return de_box

def run_test(net):
    print 'Run the net on a test image...'
    timer = Timer()
    timer.tic()
    im = 128 * np.ones((300, 500, 3), dtype=np.uint8)
    _, _ = im_detect(net, im)
    timer.toc()
    print 'Test takes',timer.total_time,'s.'

# --------------------------------------------------
#	Cloud Server
# --------------------------------------------------
app = Flask(__name__)
app.debug = DEBUG

# Methods
@app.route('/')
def run_hello():
    return 'Hello!'

@app.route('/demo', methods = ['post', 'get'])
def run_demo():
    global net
    run_test(net)
    return jsonify(info='Hello')

@app.route('/detect', methods = ['post'])
def run_detect():
    global net
    # decode request
    en_box = request.form
    box = decode_box(en_box)
    print 'Receive:',box
    img_file = request.files['img']
    img_file.save(tmp_path+'tmp.jpg')
    img = cv2.imread(tmp_path+'tmp.jpg')
    # run detect
    bbox = detection(img, box, net)
    # bbox = map(int,bbox)
    print 'Respons:',bbox
    return jsonify(bbox=bbox)

@app.route('/fulldetect', methods= ['post'])
def run_ful_detect():
    global net
    # decode request
    en_box = request.form
    box = decode_box(en_box)
    print 'Receive:',box
    img_file = request.files['img']
    img_file.save(tmp_path+'tmp.jpg')
    img = cv2.imread(tmp_path+'tmp.jpg')
    # run detect
    bbox = detection(img, box, net)
    # bbox to list
    bbox = bbox.tolist()
    return jsonify(bbox=bbox)

@app.route('/correlate', methods=['post'])
def run_co_detect():
    global net
    # decode request
    en_box = request.form
    box = decode_box(en_box)
    print 'Receive:',box
    img_file = request.files['img']
    img_file.save(tmp_path+'tmp.jpg')
    img = cv2.imread(tmp_path+'tmp.jpg')
    # run detect
    bbox = co_detection(img, box, net)
    
    print 'Respons:',bbox
    return jsonify(bbox=bbox)

if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True     # Use RPN for proposals
    args = parse_args()		# parse args
    if args.LOCAL:
        HOST = '0.0.0.0'

    net = build_net()		# prepare net
    run_test(net)		# warm-up

    app.run(host = HOST, port = PORT)
