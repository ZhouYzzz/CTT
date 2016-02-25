'''
TEST 1
======
Evaluate on the effects of lantency on accuracy.
e.g. 1s latency vs 0.1s latency
'''
import argparse
import dlib
import cv2
import numpy as np
from test.read_groundtruth import read_groundtruth
import os
from compare import overlap
#    print 'hahah'
this_file_path = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Single Tracker')
parser.add_argument('--name',type=str,help='Data Base Name')
imdb_name = parser.parse_args().name

imdb_path = os.path.join(this_file_path, '../../vot2014', imdb_name)
print imdb_path
assert os.path.exists(imdb_path)
gt = read_groundtruth(imdb_name)

initbox = gt[0,:]
i=1
img = cv2.imread(imdb_path+'/%08d.jpg'%i)

tracker = dlib.correlation_tracker()
tracker.start_track(img, dlib.rectangle(*initbox))

# modify this one
# ===============
num_frame = 100
# ===============


result = np.zeros(num_frame)


for i in xrange(num_frame):
        print 'interval', i
	t = tracker
	img = cv2.imread(imdb_path+'/%08d.jpg'%(i+1))
	t.update(img)

	rect = t.get_position()
        box = [rect.left(),rect.top(),rect.right(),rect.bottom()]
        ol = overlap(box,gt[i])
        result[i] = ol


print result
import matplotlib.pyplot as plt

plt.plot(result)
plt.xlim([0,num_frame])
plt.ylim([0,1])
plt.show()
