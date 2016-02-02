import requests
import numpy as np
import os

URL = 'http://0.0.0.0:5000/fulldetect'
this_file_path = os.path.dirname(os.path.abspath(__file__))
imdb_name = 'bolt'
imdb_path = os.path.join(this_file_path, 'img', imdb_name)

f = open(imdb_path+'/%04d.jpg'%200)
r = requests.post(url=URL, files={'img':f})
bbox = np.array(r.json()['bbox'])
print bbox
f.close()
