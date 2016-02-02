from filterpy.kalman import KalmanFilter
import numpy as np

def getPrediction(f):
	print 'Pre',f.get_prediction()[0]

def loop(f, location):
	f.predict()
	f.update([location])

if __name__ == '__main__':
	f = KalmanFilter(dim_x = 2, dim_z = 1)
	f.x = [0,0]
	f.F = np.array([
		[1,1],
		[0,1]])
	f.H = np.array([
		[1,0]])
	f.P *= 10000
	f.R *= 10
	f.Q *= 1
	for i in xrange(10):
		loop(f,0)

	for i in xrange(10):
		loop(f,10)
		getPrediction(f)

	