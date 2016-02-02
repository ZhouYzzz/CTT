import dlib
import numpy as np
from new.assign import overlap
<<<<<<< HEAD
=======
import argparse
import os, cv2
>>>>>>> 3a4cd67a9a3f16e55c65a1cb25f2644495d50ca0

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

# import numpy as np
all_gt = np.loadtxt(imdb_path+'/groundtruth.txt',delimiter=',')
<<<<<<< HEAD

t = dlib.correlation_tracker()

ol = np.zeros(img_count-10)

for i in xrange(img_count-10):
	img = cv2.imread(imdb_path+'/%08d.jpg'%(i+1))
	t.start_track(img, dlib.rectangle(*all_gt[i]))
	img2 = cv2.imread(imdb_path+'/%08d.jpg'%(i+10))
	t.update()
	rect = tracker.get_position()
    box = [int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())]
    ol[i] = overlap(box, all_gt[i+9])

import matplotlib.pyplot as plt

=======
# print all_gt.shape
all_gt = all_gt[:,[2,3,6,7]].astype(np.int)
print all_gt.shape
t = dlib.correlation_tracker()

ol = np.zeros(img_count-60)

for i in xrange(img_count-60):
	img = cv2.imread(imdb_path+'/%08d.jpg'%(i+1))
	t.start_track(img, dlib.rectangle(*all_gt[i]))
	img2 = cv2.imread(imdb_path+'/%08d.jpg'%(i+60))
	t.update(img2)
	rect = t.get_position()
        box = [int(rect.left()),int(rect.top()),int(rect.right()),int(rect.bottom())]
        ol[i] = overlap(box, all_gt[i+59])
        print 'frame',i

import matplotlib.pyplot as plt
print 'Average Acuuracy', np.average(ol)
>>>>>>> 3a4cd67a9a3f16e55c65a1cb25f2644495d50ca0
plt.plot(ol)
plt.show()
