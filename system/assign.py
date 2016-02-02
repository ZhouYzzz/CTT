import numpy as np
from munkres import Munkres

def overlap(A, B):
    [XA1, YA1, XA2, YA2] = A
    [XB1, YB1, XB2, YB2] = B
    SI = max(0,min(XA2, XB2) - max(XA1, XB1)) * \
         max(0,min(YA2, YB2) - max(YA1, YB1))
    S = area(A) + area(B) - SI
    return float(SI) / S

def area(box):
    return (box[2]-box[0])*(box[3]-box[1])

def bbox2center(bbox):
    """docstring for bbox2center"""
    return [int((bbox[0]+bbox[2])/2), int((bbox[1]+bbox[3])/2)]

def center2box(center, bbox):
    W = bbox[2]-bbox[0]
    H = bbox[3]-bbox[1]
    return [int(center[0]-W/2), int(center[1]-H/2), \
            int(center[0]+W/2), int(center[1]+H/2)]

def distance(bbox, detection):
    """docstring for distance"""
    nDetections = detection.shape[0]
    d = np.zeros(nDetections)
    D = detection - np.ones([nDetections,1])*bbox
    for i in xrange(nDetections):
        d[i] = np.linalg.norm(D[i],1)

    return d

def assignDetectionsToTracks(cost, costOfNonAssignment):
    """ Function: assignDetectionsToTracks

        assign detections to tracks for multi-object
        tracking using James Munkres' variant of the
        Hungarian  assignment  algorithem.  It  also
        determines  which  tracks  are  missing, and
        which  detections should  begin new  tracks.

        Inputs:
        -------

        Outputs:
        --------
    """
    costUnmatchedTracksVector = \
            np.ones(cost.shape[0],np.int)*costOfNonAssignment

    costUnmatchedDetectionsVector = \
            np.ones(cost.shape[1],np.int)*costOfNonAssignment

    return cvalgAssignDetectionsToTracks(cost, \
            costUnmatchedTracksVector, \
            costUnmatchedDetectionsVector)

def cvalgAssignDetectionsToTracks(cost, \
        costUnmatchedTracks, costUnmatchedDetections):
    """ Function: cvalgAssignDetectionsToTracks

        Inputs:
        -------

        Outputs:
        --------
    """
    paddedCost = getPaddedCost(cost, \
            costUnmatchedTracks, costUnmatchedDetections)

    assignments = Munkres().compute(paddedCost)
    matches = np.array(assignments)

    rowInds = matches[:,0]
    colInds = matches[:,1]

    [rows, cols] = cost.shape

    unmatchedTracks = \
            rowInds[np.where((rowInds<rows)&(colInds>=cols))]
    unmatchedDetections = \
            colInds[np.where((colInds<cols)&(rowInds>=rows))]

    matches = matches[np.where((rowInds<rows)&(colInds<cols))]

    if matches.shape[0] == 0:
        matches = np.zeros([0,2])

    return [matches, unmatchedTracks, unmatchedDetections]

def getPaddedCost(cost, \
        costUnmatchedTracks, costUnmatchedDetections):
    """getPaddedCost"""
    bigNumber = 100000

    [rows, cols] = cost.shape
    paddedSize = rows + cols
    paddedCost = np.ones([paddedSize, paddedSize],np.int)*\
            bigNumber

    paddedCost[0:rows, 0:cols] = cost

    for i in xrange(rows):
        paddedCost[i, cols+i] = costUnmatchedTracks[i]

    for i in xrange(cols):
        paddedCost[rows+i, i] = costUnmatchedDetections[i]

    paddedCost[rows:, cols:] = 0
    return paddedCost

if __name__ == '__main__':
    A = [0,0,20,50]
    B = [1,1,25,90]
    print overlap(A, B)
