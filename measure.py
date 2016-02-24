'''
measure
'''

import numpy as np

def overlap(A, B):
	[XA1, YA1, XA2, YA2] = A
	[XB1, YB1, XB2, YB2] = B
	SI = max(0,min(XA2, XB2) - max(XA1, XB1)) * \
		 max(0,min(YA2, YB2) - max(YA1, YB1))
	S = area(A) + area(B) - SI
	return float(SI) / S

def area(A):
	return (A[2]-A[0])*(A[3]-A[1])

def distance(A, B, norm=2):
	CA = box2center(A)
	CB = box2center(B)
	return np.linalg.norm(CA-CB,norm)

def box2center(A):
	[XA1, YA1, XA2, YA2] = A
	return np.array([(float(XA1)+XA2)/2, (float(YA1)+YA2)/2])

def box2size(A):
	[XA1, YA1, XA2, YA2] = A
	return np.array([XA1, YA1, XA2 - XA1, YA2 - YA1])

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
		score = np.linalg.norm(box2center(boxes[i]-grdTruth[i]),ord=2)
		count[int(np.ceil(n*score/50)):] += 1

	return count/nFrame

if __name__ == '__main__':
	A = np.array([0,0,10,10])
	B = np.array([1,1,9.125,10.187])

	print overlap(A, B)
	print area(A)
	print box2center(B)
	print box2size(B)
	print distance(A, B)