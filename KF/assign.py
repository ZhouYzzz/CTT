import numpy as np
from munkres import Munkres
import time

def distance(a1, a2):
	# print a2.shape
	nD = a2.shape[0]
	print nD
	d = np.zeros(nD)
	print d
	D = a2 - np.ones([nD,1])*a1
	print D
	for i in xrange(nD):
		d[i]=np.linalg.norm(D[i],1)
	
	return d

def assignDetectionsToTracks(cost, costOfNonAssignment):
	'''Finished'''
	costUnmatchedTracksVector = \
		np.ones(cost.shape[0],np.int)*costOfNonAssignment

	# print costUnmatchedTracksVector.shape

	costUnmatchedDetectionsVector = \
		np.ones(cost.shape[1],np.int)*costOfNonAssignment

	# print costUnmatchedDetectionsVector.shape

	return cvalgAssignDetectionsToTracks(cost, \
		costUnmatchedTracksVector, \
		costUnmatchedDetectionsVector)

def cvalgAssignDetectionsToTracks(cost, \
    		costUnmatchedTracks, \
    		costUnmatchedDetections):
	'''Cons'''
	paddedCost = getPaddedCost(cost, costUnmatchedTracks,\
		costUnmatchedDetections)
	# assert paddedCost != None

	# [rowInds, colInds] = np.argwhere(
	# 	hungarianAssignment(paddedCost))
	
	assignments = Munkres().compute(paddedCost)
	matches = np.array(assignments)
	# print matches.shape
	rowInds = matches[:,0]
	colInds = matches[:,1]
	# print rowInds, colInds

	[rows, cols] = cost.shape

	unmatchedTracks = \
		rowInds[np.where((rowInds<rows)&(colInds>=cols))]
	unmatchedDetections = \
		colInds[np.where((colInds<cols)&(rowInds>=rows))]
	# print unmatchedTracks, unmatchedDetections
	# print matches
	# print np.where((rowInds<rows)&(colInds<cols))
	matches = matches[np.where((rowInds<rows)&(colInds<cols))]
	# print matches

	# print assignments
	if matches.shape[0]==0:
		matches = np.zeros([0,2])

	return [matches,unmatchedTracks,unmatchedDetections]


def getPaddedCost(cost, costUnmatchedTracks, costUnmatchedDetections):
	'''--> cvalgAssignDetectionsToTracks'''
	bigNumber = getTheHighestPossibleCost(cost);
	# cost(isinf(cost)) = bigNumber;

	[rows, cols] = cost.shape
	# print rows, cols
	paddedSize = rows + cols
	paddedCost = np.ones([paddedSize, paddedSize],np.int) * bigNumber

	paddedCost[0:rows, 0:cols] = cost

	for i in xrange(rows):
		# print costUnmatchedTracks[i]
		paddedCost[i, cols+i] = costUnmatchedTracks[i]

	for i in xrange(cols):
		paddedCost[rows+i, i] = costUnmatchedDetections[i]

	paddedCost[rows:, cols:] = 0
	# print paddedCost
	return paddedCost

def getTheHighestPossibleCost(cost):
	'''--> getPaddedCost'''
	return 100000

if __name__ == '__main__':
	a1 = np.array([2,3,4,4])
	detection = np.array([[2,3,4,5],[1,2,3,4]])
	print distance(a1,detection)

	cost = np.array([
		[3,4,5,6],
		[5,6,7,8]])
	costOfNonAssignment = 20
	flag = time.time()
	print assignDetectionsToTracks(cost, costOfNonAssignment)
	print time.time()-flag
