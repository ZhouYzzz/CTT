import numpy as np
import os, time
import cv2, dlib
from filterpy.kalman import KalmanFilter
from new.assign import *
import requests
from multiprocessing import Queue, Process
from threading import Thread, Timer
from new.config import cfg
import argparse
from compare import success, precesion

class Track():
    """ Track Object that keep track of each object."""
    def __init__(self, ID, bbox, groundTruth=[0,0,0,0]):
        # Tracker's ID
        self.ID = ID
        # Counts
        self.age = 1
        self.AGE_THRESHOLD = 8
        self.totalVisibleCount = 1
        self.VISIBILITY_THRESHOLD = 0.6
        self.consecutiveInvisibleCount = 0
        # Status
        self.ON_TRACK = False       # managed by _KF_predict, very important
        if overlap(bbox, groundTruth) > 0.4:
            self.USE_CT  = True # should be true
            self.IS_TARGET = True
            print 'OH YOU FIND IT SUCESSFULLY'
        else:
            self.USE_CT = False
            self.IS_TARGET = False

        # Constants
        self.ON_TRACK_THRESHOLD = 0

        self.USE_KF  = True         # No use
        self.DETECTED= True         # managed by _KF_predict
        self.VISIBLE = True
        self.UPDATED = True         # SHould be True when first init
        self.UPDATE_ASSIGN = True   #'ADJUST'
        self.DISPLAY = False
        self.MISSING = False        # managed by _updateStatus, very important 
        # Boxes
        self.KF_center = bbox2center(bbox) # center: used by KF
        self.KF_center_old = self.KF_center
        self.KF_box = bbox              # MAIN box: when KF, change by KF
        self.KF_box_old = bbox
        self.CT_box = bbox
        self.CT_box_old = bbox          # old box: used when new detections came
        self.CT_box_update = bbox       # update box: used by CT
        # Objects
        self.KF = self._KF_init()        # Kalman Filter
        self.CT = self._CT_init()        # Correlation Tracker

        # self.update(bbox)               # do update after initialize
        return

    def _KF_init(self): # para: Center of box used for prediction
        KF = KalmanFilter(4,2)
        KF.x = self.KF_center + [0,0] # can be improved for accuracy e.g. from which edge
        KF.F = np.array([
            [1,0,1,0],
            [0,1,0,1],
            [0,0,1,0],
            [0,0,0,1]])
        KF.H = np.array([
            [1,0,0,0],
            [0,1,0,0]])
        KF.P *= 100
        KF.R *= 100
        # KF.Q *= 2
        # KF.predict()
        return KF

    def _CT_init(self):
        CT = dlib.correlation_tracker()
        return CT

    def update(self, detection=None):
        """ update
            ------
            The very function when the Stack receives response and then calls.
            It will do the following things:

            1.  Call // _KF_predict // to determine if predicted right and do
                new prediction as well.

            2.  Update the status of the track.

            3.  Call // _CT_preForAdjust // for preparation. Whether / Assign /
                or / Adjust/ is determined by // self.ON_TRACK //.

            4.  Call // _updateStatus // to modify other states like visibility,
                missing and so on.
        """
        # excute every time the Stack get valid response from server.

        # STEP 1:
        self._KF_predict(detection)

        # STEP 2:
        self.age += 1
        if self.DETECTED:
            self.totalVisibleCount += 1
            self.consecutiveInvisibleCount = 0
        else:
            self.consecutiveInvisibleCount += 1

        if self.USE_CT:
            self._CT_preForAdjust(detection)

        # ==== Time Point ====
        # center: Current center **predicted**
        # MAIN box: current bbox **predicted** and used for display
        # old box: last MAIN box.
        # update box: for CT to adjust

        self._updateStatus()            # update track's status
        self._KF_turn_new_to_old()      # turn new to old
        return

    def CT_run(self, img, img_old, img_last):
        """ CT_run:
            -------
            When called, it will // CT.update // the Correlation Tracker once.
            if self.UPDATED, it will call // CT.start_track //.
        """
        if self.UPDATED:
            if self.UPDATE_ASSIGN:
                self.CT.start_track(img_old, dlib.rectangle(*self.CT_box_update))
            else:
                self.CT.start_track(img_last, dlib.rectangle(*self.CT_box_update))

            self._CT_turn_new_to_old() # turn new to old
        
        self.CT.update(img)
        # get current position and update // CT_box //
        rect = self.CT.get_position()
        self.CT_box = [int(rect.left()),  int(rect.top()), \
                    int(rect.right()), int(rect.bottom())]
        if self.UPDATED:
            pass
            # _CT_turn_new_to_old()

        self.UPDATED = False

        return

    def getoldbox(self):
        if self.USE_CT:
            return self.CT_box_old
        else:
            return self.KF_box_old

    def _CT_turn_new_to_old(self):
        self.CT_box_old = self.CT_box
        return

    def _KF_turn_new_to_old(self):
        self.KF_box_old = self.KF_box
        self.KF_center_old = self.KF_center
        return

    def _updateStatus(self):
        """ updateStatus:
            -------------
            Update some status
        """
        # self.VISIBLE
        if self.consecutiveInvisibleCount >= 2:
            self.VISIBLE = False
        else:
            self.VISIBLE = True
        # self.DISPLAY
        if (self.age >= 2) & self.VISIBLE: # & self.ON_TRACK & self.VISIBLE:
            self.DISPLAY = True
        else:
            self.DISPLAY = False
        # self.MISSING
        if self.consecutiveInvisibleCount >= 5:
            print '========================='
            print 'DELETE FOR LONG INVISIBLE'
            print '========================='
            self.MISSING = True

        if (self.age < self.AGE_THRESHOLD) & \
           (self.totalVisibleCount/self.age < self.VISIBILITY_THRESHOLD):
            print '========================='
            print 'DELETE FOR LOW VISIBLITY '
            print '========================='
            self.MISSING = True

        if self.MISSING & self.IS_TARGET:
            FIND_TARGET = False
            print '!!!!!!!!!!!!!!! OH MY !!!!!!!!!!! GOD !!!!!!!'
        
        return


    def _CT_preForAdjust(self, detection=None): # CT
        """ _CT_preForAdjust:
            -----------------
            When new detection(or None) come, _CT_preForAdjust will:

            If self.ON_TRACK, then it will modify // self.CT_box_update // by
            adjusting it according to the latest CT box, old CT box and detected
            box.

            If not self.ON_TRACK, the it will assign // self.CT_box_update //
            with the latest predicted result.

            Following the 2 conditions above, it will turn // self.UPDATED //
            flag on, for Stack to use.

            If no detection come, then it will do nothing.
        """
        if self.DETECTED:
            self.UPDATED = True
            # if self.ON_TRACK:
            #     box = np.array(self.CT_box)
            detection = np.array(detection)
            box_old = np.array(self.CT_box_old)
            ol = overlap(self.CT_box_old, detection)

            #     new = box + detection - box_old
            #     self.CT_box_update = new.tolist()
            # else:
            #     self.CT_box_update = self.KF_box
            if ol > self.ON_TRACK_THRESHOLD:
            	self.CT_box_update = (self.CT_box+ol*(detection-box_old)).astype(np.int)
            	self.UPDATE_ASSIGN = False
            else:
            	self.CT_box_update = detection
            	self.UPDATE_ASSIGN = True
        	
        return

    def _KF_predict(self, detection=None): # will change self.center & box
        """ _KF_predict:
            ------------
            When new detection(or None) come, _KF_predict will:

            1.  Update // self.DETECTED // for functions' later use.
            
            2.  Determine whether the previous prediction is right or not.
                Accordingly, update // self.ON_TRACK // which indicates if the
                previous CTs actully following the object.

            3.  Use the new Detection to do the "correct and predict" of Kalman
                Filter. If detection is None, do "predict" only. Then // KF.x //
                represents the current likely state of the object.
        """
        # STEP 1:
        if detection:
            self.DETECTED = True
        else:
            self.DETECTED = False

        # STEP 2:
        # if self.DETECTED:
        #     if self.ON_TRACK:
        #         ol = overlap(self.CT_box_old, detection)
        #     else:
        #         ol = overlap(self.KF_box_old, detection)

        #     if ol > self.ON_TRACK_THRESHOLD:
        #         self.ON_TRACK = True
        #         # print '=== ON TRACK!'
        #     else:
        #         self.ON_TRACK = False
                # print 'NOT ON TRACK!'
        # else:
        #     ol = overlap(self.KF_box, self.CT_box)
        #     if ol > self.ON_TRACK_THRESHOLD:
        #         self.ON_TRACK = True
        #     else:
        #         self.ON_TRACK = False

        # STEP 3: correct and predict
        self.KF.predict()
        if self.DETECTED:
            self.KF.update(bbox2center(detection))

        self.KF_center = self.KF.get_prediction()[0][:2]
        if self.DETECTED:
            print self.KF_center - bbox2center(detection)

        if self.DETECTED:
            self.KF_box = center2box(self.KF_center, detection)
        else:
            self.KF_box = center2box(self.KF_center, self.KF_box)

        return self.KF_box  # the predicted bbox

class Stack():
    """ The very system that manage all the track objects."""
    def __init__(self, cfg=None):
        # Track Stack
        self.tracks = []
        self.trackerID = 0
        # Image
        self.img = None
        self.img_last = None
        self.img_old = None
        self.idx = 1
        self.idx_old = 1
        # Status
        self.RUN = True
        # Constants
        self.costOfNonAssignment = 100
        self.time = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
        # self.logPath = this_file_path+'/log/'+self.time

        self.logArray = np.zeros([0,5])
        self.groundTruth = self.readGroundTruth()

    def start(self):
        """docstring for start"""
        # self.buildLogPath()
        # initizalize self.img
        # self.readIMG()
        # Tracking Threading
        self.timer()
        print 'Prepared! system starts!'
        while self.RUN:     # While running
            flag = time.time()
            detection = self.postPro()  # Start Post new img
            print 'Get Response, took', time.time()-flag, 's'
            self.getDetectionResult(detection) # deal with detection result
            print 'All took', time.time()-flag, 's'

        return

    def timer(self):
        """docstring for timer"""
        if self.RUN:
            # print 'New Frame', self.idx
            flag = time.time()

            self.readIMG() # read new frame
            self.correlation_tracker() # update correlation_tracker(s)
            # self.display() # display img and boxes
            
            self.checkState()
            self.singleLog()
            # self.log()
            time_consumed = time.time() - flag
            if time_consumed > 0.04:
                print 'Time > 40 ms!'
                Timer(0, self.timer).start() # excuted instantly
            else:
                Timer(0.04 - time_consumed, self.timer).start() # excute this function every 40 ms

        return

    # def buildLogPath(self):
    #     if not os.path.exists(self.logPath):
    #         os.makedirs(self.logPath)
            # print 'Path Build', self.logPath

    def checkState(self):
        """docstring for checkState"""
        if self.idx > img_count:
            self.RUN = False

        return

    def readIMG(self):
        """docstring for readIMG"""
        # self.img_old = self.img
        self.img_last = self.img
        self.img = cv2.imread(imdb_path+'/%08d.jpg'%self.idx)
        self.idx += 1
        assert self.img != None
        # self.img = cv2.readCam()
        return

    def display(self):
        """docstring for display"""
        for track in self.tracks:
            if track.DISPLAY:
                bbox = track.box
                pt1 = (bbox[0],bbox[1])
                pt2 = (bbox[2],bbox[3])
                cv2.rectangle(self.img, pt1, pt2, (255,255,255), 2)
                # pass # we will display its bbox

        cv2.imshow('Vedio', self.img)
        cv2.waitKey(1)
        print 'SHOW'
        return

    def log(self):
        """docstring for log"""
        # allbox = np.zeros([0,4],np.int) # prepare an empty array
        for track in self.tracks:
            if True:
                self.logArray = np.vstack([self.logArray,\
                        np.append(self.idx,track.KF_box)])

        if ~self.RUN:
            np.savetxt('logfile/'+self.time, self.logArray.astype(np.int),fmt='%d')

    def singleLog(self):
        for track in self.tracks:
            if track.IS_TARGET:
                # print track.ON_TRACK, track.VISIBLE, track.MISSING
                self.logArray = np.vstack([self.logArray,\
                        np.append(self.idx,track.CT_box)])

        if ~self.RUN:
            np.savetxt('logfile/'+self.time, self.logArray.astype(np.int),fmt='%d')

    def correlation_tracker(self):
        """docstring for correlation_tracker"""
        for track in self.tracks:
            if track.USE_CT:
                assert self.img != None
                assert self.img_old != None
                track.CT_run(self.img, self.img_old, self.img_last) # update tracks

        return

    def postImg(self,queue):
        """docstring for postImg"""
        f = open(imdb_path+'/%08d.jpg'%self.idx)
        # self.idx_old = self.idx
        # self.idx_old = self.idx # mark down this moment
        # self.img_old = self.img
        r = requests.post(url=URL, files={'img':f})
        detection = r.json()['bbox']
        detection = np.array(detection, np.int)
        queue.put(detection)
        f.close()
        return

    def postPro(self):
        """docstring for postPro"""
        # New Process to post image
        print 'Post a new img', self.idx
        self.idx_old = self.idx
        self.img_old = self.img
        q = Queue()
        p = Process(target=self.postImg,args=[q])
        p.start()
        p.join(0.6) # timeout 600 ms
        return q.get()

    def getDetectionResult(self, detection):
        """docstring for getDetectionResult"""
        if detection.shape[0] == 0:
            detection = np.zeros([0,4])

        [assignments, unassignedTracks, unassignedDetections] = \
                self.detectionToTrackAssignment(detection)

        self.updateAssignedTracks(assignments, detection)
        self.updateUnassignedTracks(unassignedTracks)
        self.deleteLostTracks()
        self.createNewTracks(unassignedDetections, detection)
        return

    def detectionToTrackAssignment(self, detection):
        """docstring for detectionToTrackAssignment"""
        # Number of tracks and detections
        nTracks = len(self.tracks)
        print 'Now', nTracks, 'tracker(s).'
        nDetections = detection.shape[0]
        print 'New', nDetections, 'object(s).'

        # Compute cost matrix
        cost = np.zeros([nTracks, nDetections], np.int)
        for i in xrange(nTracks):
            cost[i, :] = distance(self.tracks[i].getoldbox(), detection)

        # assign Detections to Tracks
        costOfNonAssignment = self.costOfNonAssignment
        return assignDetectionsToTracks(cost, costOfNonAssignment)

    def updateAssignedTracks(self, assignments, detection):
        """docstring for updateAssignedTracks"""
        numAssignedTracks = assignments.shape[0]
        for i in xrange(numAssignedTracks):
            trackIdx = assignments[i,0]
            detectionIdx = assignments[i,1]
            bbox = detection[detectionIdx,:]

            track = self.tracks[trackIdx]

            # update the track with detection
            track.update(bbox.tolist())

        return

    def updateUnassignedTracks(self, unassignedTracks):
        """docstring for updateUnassignedTracks"""
        for i in xrange(len(unassignedTracks)):
            idx = unassignedTracks[i]
            track = self.tracks[idx]

            # update the track without detection
            track.update()

        return

    def deleteLostTracks(self):
        """docstring for deleteLostTracks"""
        for track in self.tracks:
            if track.MISSING:
                self.tracks.remove(track)

        return

    def createNewTracks(self, unassignedDetections, detection):
        """docstring for createNewTracks"""
        bboxes  = detection[unassignedDetections, :]
        nNew = bboxes.shape[0]

        for i in xrange(nNew):
            bbox = bboxes[i,:].tolist()
            if not FIND_TARGET:
                track = Track(self.trackerID, bbox, self.groundTruth[self.idx_old])
            else:
                track = Track(self.trackerID, bbox)
            self.tracks.append(track)
            self.trackerID += 1

        return

    def readGroundTruth(self):
        gt = np.loadtxt(imdb_path+'/groundtruth.txt',delimiter=',')
        gt = gt[:,[2,3,6,7]].astype(np.int)
        return gt
        # gt = [gt[2], gt[3], gt[6], gt[7]]
        # return map(int,gt)

    def getTargetTrack(self):
        for track in self.tracks:
            if track.IS_TARGET:
                return track

        return None


if __name__ == '__main__':

	FIND_TARGET = False

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

        URL = cfg.URL

        print 'Demo Start'
        stack = Stack()
        stack.start()
        # print stack.readGroundTruth()
        print 'Finished'
