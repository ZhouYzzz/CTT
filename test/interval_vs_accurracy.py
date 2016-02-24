'''
TEST 1
======
Evaluate on the effects of lantency on accuracy.
e.g. 1s latency vs 0.1s latency
'''
import argparse
from tools import read_groundtruth
import dlib
import cv2
import numpy as np

parser.add_argument('--name',type=str,help='Data Base Name')
imdb_name = parser.parse_args().name
imdb_path = os.path.join(this_file_path, '../vot2014', imdb_name)
assert os.path.exists(imdb_path)


gt = read_groundtruth(imdb_name)

initbox = gt[0,:]

tracker = dlib.correlation_tracker()
tracker.start_track(img, dlib.rectangle(*initbox))

result = np.zeros(50)

for i in xrange(50):
	t = tracker
	img = cv2.imread(imdb_path+'/%08d.jpg'%i)
	t.update(img)

	rect = t.get_position()
    box = [int(rect.left()), int(rect.top()),\
            int(rect.right()), int(rect.bottom())]
    ol = overlap(box,gt[idx])
    result[i] = ol

import matplotlib.pyplot as plt

plt.plot(ol)

plt.show()