'''
compare
'''

from client.assign import overlap
import numpy as np

def success(boxes, grdTruth, n=100):
	assert boxes.shape == grdTruth.shape
	nFrame = boxes.shape[0]
	count = np.zeros(n)
	for i in xrange(nFrame):
		score = overlap(boxes[i], grdTruth[i])
		count[:int(np.floor(n*score))] += 1

	return count/nFrame


def precesion(boxes, grdTruth, n=100):
	assert boxes.shape == grdTruth.shape
	nFrame = boxes.shape[0]
	count = np.zeros(n)
	for i in xrange(nFrame):
		score = np.linalg.norm(boxes[i]-grdTruth[i],ord=2)
		count[int(np.ceil(n*score/50)):] += 1

	return count/nFrame

if __name__ == '__main__':
	# print 'Nothing happened'
	boxes = np.array([[10,10,20,20],
		[10,10,30,30],
		[0,0,1,1],
		[2,3,100,100]])
	grdTruth = np.array([[10,10,25,20],
		[20,20,40,40],
		[1,1,2,2],
		[1,2,200,100]])
	print success(boxes,grdTruth,10)
	print precesion(boxes,grdTruth)
	# print success(boxes,boxes)