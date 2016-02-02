# import dlib
from config import cfg

class Track():
	def __init__(self, ID):
		self.ID = ID
		self._tracker = dlib.correlation_tracker()
		self.box = []
		self.box_old = []
		self.box_update = []
		self.UPDATED = True

	def update(self, img, img_old):
		if self.UPDATED:
			''' call < tracker.start_track > method '''
			self._tracker.start_track(img_old, \
				dlib.rectangle(*self.box_update))
		
		''' call < tracker.update > method '''
		self._tracker.update(img)

	def prepare_for_update(self, detection):
		pass
		

class Stack():
	def __init__(self):
		self.tracks = []
		self.RUN = False

	def run(self):
		self.RUN = True
		while self.RUN:
			''''''

if __name__ == '__main__':
	stack = Stack()
