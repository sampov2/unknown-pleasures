#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/scale_results.py


import trimesh 
import math
from shapely.geometry import Polygon, Point
import shapely
from svglib.svglib import svg2rlg
from reportlab.graphics import shapes;
from transforms3d.euler import euler2mat;

import numpy as np
from scipy import interpolate

models = [
	"unknown_pleasures_face_mould.stl",
	"unknown_pleasures_inner_mould.stl",
	"unknown_pleasures_outer_mould.stl",
	"unknown_pleasures_positive.stl"
]

def scale_matrix(s):
	return ((s, 0, 0, 0),
		  	(0, s, 0, 0),
			(0, 0, s, 0),
		  	(0, 0, 0, 1))

scale_factor = .2
matrix = scale_matrix(scale_factor)

for file in models:
	filename = '/models/{}'.format(file)
	print("Scaling {}".format(filename))
	mesh = trimesh.load(filename)
	mesh.apply_transform(matrix)
	mesh.export(filename)

