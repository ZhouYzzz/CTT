class A():
	def __init__(self, ID):
		self.ID = ID
		self.sth = self.load()

	def load(self):
		print self.ID

A(5)