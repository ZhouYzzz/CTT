'''
analyse result
'''

import argparse
import os
import numpy as np
from compare import precesion, success
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Single Tracker')
parser.add_argument('--name',type=str,help='Data Base Name')
parser.add_argument('--log', type=str,help='Log')

imdb_name = parser.parse_args().name
logfile = parser.parse_args().log
print 'Name:', imdb_name
print 'Logfile:', logfile


# global varibles
# print 'Modules prepared, Demo starts...'
this_file_path = os.path.dirname(os.path.abspath(__file__))
# imdb_name = 'car'
imdb_path = os.path.join(this_file_path, '../vot2014', imdb_name)
logfile_path = os.path.join(this_file_path,'logfile', logfile)

print 'IMG path:', imdb_path
assert os.path.exists(imdb_path)
_, _, files = os.walk(imdb_path).next()
img_count = len(files) - 7
print 'IMG count:', img_count

all_gt = np.loadtxt(imdb_path+'/groundtruth.txt',delimiter=',')
result = np.loadtxt(logfile_path)

# print result[:,0]

gt = all_gt[result[:-1,0].astype(np.int)-1,:]
#print gt
gt = gt[:,[2,3,6,7]]
print gt

boxes = result[:-1,1:]

su = success(boxes,gt,100)
# su = precesion(boxes,gt,100)

plt.plot(su)
plt.show()
