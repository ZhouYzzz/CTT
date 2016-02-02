#!/bin/bash

# set -x
set -e

# SETUP CAFFE
export PYTHONPATH=/home/yaos11/yao/caffe.backup/python:$PYTHONPATH

# SETUP CUDA LIB
export LD_LIBRARY_PATH=/opt/cuda-6.5/lib64:$LD_LIBRARY_PATH

echo SETUP!
