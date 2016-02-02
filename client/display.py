import numpy as np
import argparse
import cv2

def display(data, database):
    line = 0
    while True:
        idx = data[line,0]
        img = cv2.imread(database+'%08d.jpg'%(idx))
        while data[line,0]==idx:
	    bbox = data[line,1:]
	    # img = cv2.imread(database+'%08d.jpg'%idx)
	    pt1 = (int(bbox[0]),int(bbox[1]))
            pt2 = (int(bbox[2]),int(bbox[3]))
            cv2.rectangle(img, pt1, pt2, (255,255,255), 2)
            line += 1
            
        cv2.imshow('Vedio', img)
        cv2.waitKey(1)

    return

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--file')
	parser.add_argument('--data')
	# parser.add_argument('--count')

	args = parser.parse_args()
	logfile = args.file
	basename = args.data
	# count = args.count
	assert logfile is not None
	assert basename is not None
	datapath = '/home/yaos11/zhouyz/vot2014/'
	database = datapath + basename + '/'
	print 'Data Base:', database
	data = np.loadtxt(logfile)
	print data[1]
	print 'Display!!!'

	display(data, database)
