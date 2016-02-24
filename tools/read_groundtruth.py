def read_groundtruth(name):
	assert type(name) == str
	this_file_path = os.path.dirname(os.path.abspath(__file__))
    # imdb_name = 'car'
    imdb_path = os.path.join(this_file_path, '../../vot2014', name)

    print 'IMG path:', imdb_path
    assert os.path.exists(imdb_path)

    import numpy as np
    all_gt = np.loadtxt(imdb_path+'/groundtruth.txt',delimiter=',')
    #gt = all_gt[0].astype(np.int)
    all_gt = all_gt.astype(np.int)
    # [gt[2],gt[3],gt[6],gt[7]]
    gt = all_gt[:,[2,3,6,7]]
    return gt

if __name__ == '__main__':
	read_grountruth()