# from KF.server_kalman_filter import Stack, Track
import numpy as np
# import dlib
import os, sys
import argparse
import requests
from multiprocessing import Process, Queue
import time

# Cloud Server
URL = 'http://yaolaoban.eva0.nics.cc:5000/detect'
# global varibles
# this_file_path = os.path.dirname(os.path.abspath(__file__))
# imdb_name = 'Jumping'
# imdb_path = os.path.join(this_file_path, 'img', imdb_name)
# _, _, files = os.walk(imdb_path).next()
# img_count = len(files) - 1
i = 1

# Status varibles
updated = False

def postIMG():
	global i, updated
	f = open(imdb_path+'/%04d.jpg'%i)
	r = requests.post(url=URL, files={'img':f})
	updtbox = r.json()['bbox']
	updated = True
	f.close()

def realtime_simulation(queue):
	while queue.get() < 100:
		queue.put(queue.get() + 1)
		print 'New Frame', i
		time.sleep(0.04)

if __name__ == '__main__':
	q = Queue()
	q.put(1)
	print q.get()
	q.put(2)
	print q.get()
	# p = Process(target=realtime_simulation, args=[q])
	# p.start()
	# print 'Started'
	# p.join()
	# print 'Joined'