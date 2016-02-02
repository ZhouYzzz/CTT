import numpy as np
import time
from assign import *
from filterpy.kalman import KalmanFilter
import cv2
from multiprocessing import Queue, Process
from threading import Thread, Timer
import dlib
import requests
import os

data_path = '/Users/zhouyizhuang/Desktop/detection_data/bolt_with_nms/'
# data_path = '/home/yaos11/yao/py-faster-rcnn/tools/logfile/bolt_with_nms/'

URL = 'http://0.0.0.0:5000/fulldetect'

this_file_path = os.path.dirname(os.path.abspath(__file__))
imdb_name = 'bolt'
imdb_path = os.path.join(this_file_path,'..', 'img', imdb_name)
_, _, files = os.walk(imdb_path).next()
img_count = len(files) - 1

idx = 1
old_idx = 1
log = np.zeros([61,5])
tracker_id = 1

def readbox(idx):
	file_name = data_path + '15_%04d' % idx
	data = np.loadtxt(file_name)
	# data = np.array(data,np.int)
	data = thresFilter(data)
	return np.array(data,np.int)

def thresFilter(box,thres=0.6):
	remain = np.where(box[:,4]>thres)
	remained_box = box[remain,:]
	return remained_box

def readframe():
	global idx, old_idx
	print '=========='
	print 'Frame Now', idx
	old_idx = idx
	idx = idx + 10

class Track():
	def __init__(self, id, location, tracker=None):
		self.id = id
		self.bbox = location
		self.oldbox = location
		self.KF = self.initFilter(location)
		self.updated = False
		self.updatebox = []
		self.state = 'off' # 'on'
		self.source = 'detection' # 'tracking'
		self.visible = 'on' # 'off'
		self.age = 1
		self.totalVisibleCount = 1
		self.consecutiveInvisibleCount = 0
		self.tracker = tracker

	def useTracker(self):
		self.source = 'tracking'
		self.tracker = initTracker()

	def notuseTracker(self):
		self.source = 'detection'
		self.tracker = None
		
	def initTracker(self):
		return dlib.correlation_tracker()

	def initFilter(self, location):
		KF = KalmanFilter(8, 4)
		KF.x = location + [0,0,0,0]
		KF.F = np.array([
			[1, 0, 0, 0, 1, 0, 0, 0],
			[0, 1, 0, 0, 0, 1, 0, 0],
			[0, 0, 1, 0, 0, 0, 1, 0],
			[0, 0, 0, 1, 0, 0, 0, 1],
			[0, 0, 0, 0, 1, 0, 0, 0],
			[0, 0, 0, 0, 0, 1, 0, 0],
			[0, 0, 0, 0, 0, 0, 1, 0],
			[0, 0, 0, 0, 0, 0, 0, 1]])
		KF.H = np.array([
			[1, 0, 0, 0, 0, 0, 0, 0],
			[0, 1, 0, 0, 0, 0, 0, 0],
			[0, 0, 1, 0, 0, 0, 0, 0],
			[0, 0, 0, 1, 0, 0, 0, 0]])
		KF.P *= 100
		KF.predict()
		# KF.update(location)
		return KF

	def check(self):
		return 'off'

	def update(self, detection=None):
		self.oldbox = self.bbox
		self.state = self.check()
		if detection is None:
			self.KF.predict()
			self.bbox = self.KF.x[:4]
		else:
			if self.state == 'off':
				self.bbox = self.predict(detection)
			else:
				self.bbox = self.adjust(detection)

	def predict(self, detection):
		self.KF.update(detection)
		self.KF.predict()
		return self.KF.x[:4]
		# return predictedLocation

	def adjust(self, detection):
		trd = Thread(target=obj_tracking)
		trd.start()

	def getlocation(self):
		return self.KF.x[:4]
			

class Stack():
	def __init__(self):
		self.tracks = []
		self.img = None
		self.oldimg = None
                self.idx = 1
		# self.tracks.append(Track(1, [267,36,296,85]))
		# self.tracks.append(Track(2, [1,1,1,10]))

	def start(self):
		# global idx
                self.timer()
		while self.idx<100: # while working
		# while idx<351:
                        flag = time.time()
			detection = self.postProcess() # timeout 0.5s
                        # print detection
			detection = np.array(detection,np.int)
                        # self.idx += 3
                        # print 'Detection:', detection
                        self.getbox(detection)
                        # print self.idx, time.time()-flag
	
	def diaplay(self):
	    for track in self.tracks:
	    	box = track.bbox
	    	pt1 = (int(box[0]),int(box[1]))
	    	pt2 = (int(box[2]),int(box[3]))
	    	cv2.rectangle(self.oldimg,pt1,pt2,(255,255,255),3)

	    cv2.imshow(self.oldimg)
	    cv2.waitKey(1)

	def timer(self):
            if self.idx < 100:
	        	self.idx += 1
	        	self.oldimg = self.img
                        # print imdb_path+'/%04d'%self.idx
	        	self.img = cv2.imread(imdb_path+'/%04d.jpg'%self.idx)
                        assert self.img != None
                        # print self.idx
                        self.correlation_tracker()
	        	Timer(0.04, self.timer).start()                 

	def correlation_tracker(self):
		flag = time.time()
		for track in self.tracks:
			if track.source == 'tracking':
				if track.updated:
                                        print '===!!!==='
                                        print 'Track updated!!!'
					# use .start_tracking method
					track.tracker.start_track(self.img, \
						dlib.rectangle(*track.updatebox))
					track.updated = False
				else:
					# use .update method
					track.tracker.update(self.img)
				
				        rect = track.tracker.get_position()
				        track.bbox = [int(rect.left()),\
							  int(rect.top()), \
							  int(rect.right()),\
							  int(rect.bottom())]
			        
                                print 'Track one frame', time.time()-flag
                        else:
				# do nothing
				pass

		

	def postIMG(self, queue):
                # print 'Post', self.idx
		f = open(imdb_path+'/%04d.jpg'%self.idx)
		r = requests.post(url=URL,files={'img':f})
		detection = r.json()['bbox']
		queue.put(detection)
		f.close()
		return

	def postProcess(self):
		q = Queue()
		p = Process(target=self.postIMG,args=[q])
		p.start()
		p.join(1) # timeout = 500ms
		return q.get()

	def getbox(self, detection):
		flag = time.time()
		[assignments, unassignedTracks, unassignedDetections] \
			= self.detectionToTrackAssignment(detection)
		
		print unassignedTracks
		self.updateAssignedTracks(assignments, detection)
		self.updateUnassignedTracks(unassignedTracks)
		self.deleteLostTracks()
		self.createNewTracks(unassignedDetections, detection)
		# self.addtracking()
		# self.predictNewLocationsOfTracks()
		print time.time()-flag

	def addtracking(self):
		if self.tracks:
			print 'Add Tracking'
			self.tracks[0].source = 'tracking'  

	def detectionToTrackAssignment(self, detection):
		# print detection.shape
		nTracks = len(self.tracks)
		print 'Now have', nTracks, 'tracker(s).'
		nDetections = detection.shape[0]
		print 'New detection have', nDetections, 'object(s).'
		cost = np.zeros([nTracks, nDetections], np.int)
		for i in xrange(nTracks):
			# print detection[:,:,:4]
                        cost[i, :] = distance(self.tracks[i].bbox, detection) #detection[:,:,:4]

		# << codes here >
		# print '---',cost
		costOfNonAssignment = 30
		return assignDetectionsToTracks(cost, costOfNonAssignment)
		
	def updateAssignedTracks(self, assignments, detection):
		numAssignedTracks = assignments.shape[0]
		for i in xrange(numAssignedTracks):
			trackIdx = assignments[i,0]
			detectionIdx = assignments[i,1]
			bbox = detection[detectionIdx,:]

			# print '!!!', bbox
			_track = self.tracks[trackIdx]

                        # delete it!!
                        if i == 1:
                            _track.source = 'tracking'

			if _track.source == 'tracking':
                                print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
				_track.updated = True
				_track.updatebox = bbox.tolist()
			else:
				_track.update(bbox)
			# print '===!!!===',
			# predict with update
			
			_track.age += 1
			_track.totalVisibleCount += 1
			_track.consecutiveInvisibleCount = 0

			
	def updateUnassignedTracks(self, unassignedTracks):
		for i in xrange(len(unassignedTracks)):
			ind = unassignedTracks[i]
			_track = self.tracks[ind]

			# predict without update
			_track.update()
			_track.age += 1
			_track.consecutiveInvisibleCount += 1

	def deleteLostTracks(self):
		if not self.tracks:
			return

		invisibleForTooLong = 1
		ageThreshold = 8

		ages = []
		totalVisibleCounts = []
		visibility = []
		invisible = []

		for _track in self.tracks:
			_age = _track.age
			_totalVisibleCount = _track.totalVisibleCount
			ages += [_age]
			totalVisibleCounts += [_totalVisibleCount]
			visibility += [_totalVisibleCount/_age]
			invisible += [_track.consecutiveInvisibleCount]

		ages = np.array(ages)
		totalVisibleCounts = np.array(totalVisibleCounts)
		invisible = np.array(invisible)
		print invisible
		lostIdx = np.logical_or((invisible > invisibleForTooLong),\
			np.logical_and((ages<ageThreshold),(visibility<0.6)))
		print lostIdx
		lost_list = np.where(lostIdx)[0].tolist()
		print lost_list
		length = len(lost_list)
		print length
		for idx in xrange(length-1,-1,-1):
			print 'idx', lost_list[idx]
			self.tracks.pop(lost_list[idx])

		return

	def createNewTracks(self, unassignedDetections, detection):
		global tracker_id
                print detection
                print unassignedDetections
		bboxes = detection[unassignedDetections,:]
		n = bboxes.shape[0]

		for i in xrange(n):
			bbox = bboxes[i,:].tolist()
			track = Track(tracker_id, bbox, dlib.correlation_tracker())
			tracker_id += 1
			self.tracks.append(track)

                        # delete below!!!
                        
		
			
	def predictNewLocationsOfTracks(self):
		global log, idx
		if self.tracks:
			#log[idx,0] = self.tracks[0].consecutiveInvisibleCount
			#log[idx,:4] = self.tracks[1].bbox[:4]
			#log[idx,4] = self.tracks[1].consecutiveInvisibleCount

			if True:
				img = cv2.imread('/home/yaos11/zhouyz/CTT/img/bolt/%04d.jpg'%self.idx)
				assert img != None
                                # print '===!!!===!!!===', img.shape
                                for track in self.tracks:
					box = track.bbox
					pt1=(int(box[0]),int(box[1]))
					pt2=(int(box[2]),int(box[3]))
					cv2.rectangle(img,pt1,pt2,(255,255,255),3)
					
				cv2.imshow('Vedio',img)
				cv2.waitKey(1)

def realtime_simulation(stack):
	while stack.idx < 100:
            print stack.idx
            stack.idx += 1
            time.sleep(0.04)

	print 'Database Over!'
	print '--------------'

def main():
	stack = Stack()
	print 'Tracks initialized'
	flag_1 = time.time()
	while idx < 30:
		readframe()
		print 'Send Frame', old_idx
		# Time delay
		# time.sleep(1)
		print 'New Detection Come, Callback'
		box = readbox(old_idx)
		# print box.shape
		stack.getbox(box)
	# print len(stack.tracks)
	# print 'Takes average', (time.time()-flag_1)/60
	# print log

if __name__ == '__main__':
	print '----------'
	print 'Demo Start'
	print '----------'

	stack = Stack()
        # p_real = Process(target=realtime_simulation,args=[stack])
	# p_real.start()
       
        stack.start()

        # p_real.join()

	print '----------'
	print ' Finished '
	print '----------'
	# flag = time.time()
	# track = Track(1,[2,2,2,2])
	# print track.predict([4,4,3,3])
	# print track.predict([5,5,4,4])
	# print track.predict([6,6,5,5])
	# print time.time()-flag


