#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen_moulds.py

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh
import math
import numpy as np


box_width_axis = 0
box_height_axis = 1
depth_axis = 2

print("loading meshes")
mesh = pymesh.load_mesh("/models/unknown_pleasures_positive.stl")

print("calculating moulds")
def generate_info(mesh):
	ret = {
		'min': np.minimum.reduce(mesh.vertices),
		'max': np.maximum.reduce(mesh.vertices),
	}
	return ret

axis_info = generate_info(mesh)
print(axis_info)

outer_mould_thickness = 10
inner_mould_thickness = 10
face_mould_thickness = 60
gap_between_moulds = .5

def gen_box(axis_info, thickness, mould_top_rel, draft_angle=0.0, extra_depth=0.0, depth_offset=0.0):
	mould_top = axis_info['min'][depth_axis] + (axis_info['max'][depth_axis] - axis_info['min'][depth_axis]) * mould_top_rel + extra_depth

	box = pymesh.generate_box_mesh([
		axis_info['min'][0] - thickness,
		axis_info['min'][1] - thickness,
		axis_info['min'][2] - thickness - depth_offset,
	],[
		axis_info['max'][0] + thickness,
		axis_info['max'][1] + thickness,
		mould_top - depth_offset,
	])

	alpha = draft_angle
	box_height = abs(mould_top -  (axis_info['min'][2] - thickness)) + extra_depth
	if abs(alpha) > 0:
		beta = 180 - 90 - alpha
		#a = box_height
		# tan(beta) = a / c
		# c * tan(beta) = a
		# c = a / tan(beta)
		# draft_offset = c = a / tan(beta)

		draft_offset = box_height / math.tan(beta * math.pi / 180)

		print('box_height = {}, draft_angle = {} (deg) => draft_offset = {}'.format(box_height, draft_angle, draft_offset))

		x_mid = (axis_info['min'][0] + axis_info['max'][0])/2
		y_mid = (axis_info['min'][1] + axis_info['max'][1])/2


		modified_vertices = np.copy(box.vertices)
		for i in range(len(modified_vertices)):
			v = modified_vertices[i]
			if abs(v[2] - axis_info['min'][2] - thickness) < abs(v[2] - mould_top):
				x_direction = 1
				y_direction = 1
				if v[0] > x_mid:
					x_direction = -1
				if v[1] > y_mid:
					y_direction = -1

				v[0] = v[0] + draft_offset * x_direction
				v[1] = v[1] + draft_offset * y_direction

		box = pymesh.form_mesh(modified_vertices, box.faces)


	return box

inner_mould = gen_box(axis_info, inner_mould_thickness, .58, draft_angle=3)

inner_mould_plus_gap = gen_box(axis_info, inner_mould_thickness + gap_between_moulds, .58, draft_angle=3)
outer_mould = gen_box(axis_info, inner_mould_thickness + outer_mould_thickness + gap_between_moulds, .58)

outer_mould = pymesh.boolean(outer_mould, inner_mould_plus_gap, operation="difference")
inner_mould = pymesh.boolean(inner_mould, mesh, operation="difference")

face_mould = gen_box(axis_info, 0, 0, extra_depth=face_mould_thickness, depth_offset=10)
face_mould = pymesh.boolean(face_mould, mesh, operation="difference")

print("writing output")
pymesh.save_mesh("/models/unknown_pleasures_outer_mould.stl", outer_mould)
pymesh.save_mesh("/models/unknown_pleasures_inner_mould.stl", inner_mould)
pymesh.save_mesh("/models/unknown_pleasures_face_mould.stl", face_mould)


positive_width  = axis_info['max'][0]-axis_info['min'][0]
positive_height = axis_info['max'][1]-axis_info['min'][1]

print("positive width {:.2f}, height {:.2f}".format(positive_width, positive_height))

print("inner mould thickness {} units ({:.2f}% of width, {:.2f}% of height)".format(inner_mould_thickness,100 * inner_mould_thickness / positive_width, 100* inner_mould_thickness / positive_height))
print("outer mould thickness {} units ({:.2f}% of width, {:.2f}% of height)".format(outer_mould_thickness,100 * outer_mould_thickness / positive_width, 100* outer_mould_thickness / positive_height))

