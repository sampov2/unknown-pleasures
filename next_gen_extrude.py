#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen_extrude.py 

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

km = KMeans(n_clusters=2, random_state=3)
km = km.fit(d_verts)

## TODO: this does not work perfectly just yet...
pred = km.predict(d_verts)

print('transforming faces')
transform_amount = 50

samples = [0, 0]

maximum = np.maximum.reduce(d_verts)

for i in range(len(pred)):
	x = pred[i]
	if x == 0:
		samples[0] = d_verts[i]
	elif x == 1:
		samples[1] = d_verts[i]
	else:
		raise Exception('Prediction {} illegal (should be 0 or 1)'.format(x))

if samples[1] > samples[0]:
	transform_direction = 1
	transform_label = 1
	base_z = np.maximum.reduce(d_verts)[0]  + transform_amount * transform_direction
else:
	transform_direction = -1
	transform_label = 0
	base_z = np.minimum.reduce(d_verts)[0]  + transform_amount * transform_direction

#transform_direction = (samples[1] > samples[0]) ? 1 : -1
verts = np.copy(mesh.vertices)


for i in range(len(pred)):
	x = pred[i]
	if x == transform_label:
		# Force the other verts to the same z-level
		verts[i, transform_axis] = base_z

updated_mesh = pymesh.form_mesh(verts, mesh.faces)

#print("cleaning up mesh")
#[updated_mesh, info] = pymesh.remove_isolated_vertices(updated_mesh)
#print("- remove_isolated_vertices: {}".format(info))
#
#[updated_mesh, info] = pymesh.remove_duplicated_vertices(updated_mesh,tol=1e-2)
#print("- remove_duplicated_vertices: {}".format(info))
#
#[updated_mesh, info] = pymesh.collapse_short_edges(updated_mesh)
#print("- collapse_short_edges: {}".format(info))
#
#[updated_mesh, info] = pymesh.remove_duplicated_faces(updated_mesh)
#print("- remove_duplicated_faces: {}".format(info))




print("writing output")
pymesh.save_mesh("/models/next_gen_output_extruded.stl", updated_mesh)

