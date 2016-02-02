import time, threading

def foo():
	print time.ctime()
	threading.Timer(0.1,foo).start()

foo()