from filterpy.kalman import KalmanFilter
import numpy as np

data = np.array([10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100])
noise = np.array([1,-1,0, -1, 1, 2, 0,-1, 1,-2,-1,-1,0, 1, 1,-2, 1,0, 0])
impluse = np.array([0,0,0,0,0,0,0,0,0,0,10,10,10,10,10,10,10,10,10])
print data + noise + impluse


def state(f):
	print f.x, f.y

if __name__ == '__main__':
	f = KalmanFilter(dim_x=4, dim_z=2)
	f.x = np.array([2,2,0,0])
	f.F = np.array([
		[1,0,1,0],
		[0,1,0,1],
		[0,0,1,0],
		[0,0,0,1]])
	f.H = np.array([
    	[1,0,0,0],
    	[0,1,0,0]])
	f.P *= 100
	f.R *= 100
	print 'Pre',f.get_prediction()[0]
	f.predict()
	# f.update([2,2])
	# state(f)
	f.update([2,2])
	print 'Pre',f.get_prediction()[0]
	f.predict()
	# f.update([2,2])
	# state(f)
	f.update([3.1,3])
	# state(f)
	print 'Pre',f.get_prediction()[0]
	f.predict()
	f.update([3.9,4])
	print 'Pre',f.get_prediction()[0]
	f.predict()
	f.update([5,5.1])
	print 'Pre',f.get_prediction()[0]
	f.predict()
	f.update([6.2,6])
	print 'Pre',f.get_prediction()[0]
	f.predict()
	print 'Pre',f.get_prediction()[0]

