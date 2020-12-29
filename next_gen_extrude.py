#!/usr/bin/python2

## docker run -it --rm -v `pwd`:/models pymesh-sklearn python /models/next_gen_extrude.py 

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh;
from sklearn.cluster import KMeans
import numpy as np

transform_axis = 2

print("loading meshes")
mesh = pymesh.load_mesh("/models/next_gen_output.stl")

#d_verts = np.copy(mesh.vertices)

d_verts = np.array([ x[transform_axis] for x in mesh.vertices ]).reshape(-1,1)

print('analyzing {} vertices'.format(len(d_verts)))

km = KMeans(n_clusters=2, random_state=1)
km = km.fit(d_verts)

pred = km.predict(d_verts)

print('transforming faces')
transform_amount = 50

samples = [0, 0]


for i in range(len(pred)):
	x = pred[i]
	if x == 0:
		samples[0] = d_verts[i]
	elif x == 1:
		samples[1] = d_verts[i]
	else:
		raise Exception('Prediction was not 0 or 1 but {}'.format(x))

if samples[1] > samples[0]:
	transform_direction = 1
else:
	transform_direction = -1

#transform_direction = (samples[1] > samples[0]) ? 1 : -1
verts = np.copy(mesh.vertices)


for i in range(len(pred)):
	x = pred[i]
	if x == 1:
		verts[i, transform_axis] = verts[i, transform_axis] + transform_amount * transform_direction


updated_mesh = pymesh.form_mesh(verts, mesh.faces)

print("writing output")
pymesh.save_mesh("/models/next_gen_output_extruded.stl", updated_mesh)

