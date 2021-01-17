#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/stl_extent.py

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh
import math
import numpy as np
import sys

print('args',sys.argv)

for i in range(1,len(sys.argv)):
	file = sys.argv[i]
	mesh = pymesh.load_mesh(file)

	def generate_info(mesh):
		ret = {
			'min': np.minimum.reduce(mesh.vertices),
			'max': np.maximum.reduce(mesh.vertices),
		}
		ret['width']  = ret['max'][0] - ret['min'][0]
		ret['height'] = ret['max'][1] - ret['min'][1]
		ret['depth']  = ret['max'][2] - ret['min'][2]
		return ret

	axis_info = generate_info(mesh)

	print('{}: width {:.2f}, height {:.2f}, depth {:.2f}'.format(file, axis_info['width'],axis_info['height'],axis_info['depth']))
