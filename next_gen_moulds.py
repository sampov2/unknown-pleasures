#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen_moulds.py

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh;
import numpy as np


box_width_axis = 0
box_height_axis = 1
depth_axis = 2

print("loading meshes")
mesh = pymesh.load_mesh("/models/next_gen_output_extruded.stl")

print("calculating moulds")
def generate_info(mesh):
	ret = {
		'min': np.minimum.reduce(mesh.vertices),
		'max': np.maximum.reduce(mesh.vertices),
	}
	return ret

axis_info = generate_info(mesh)
print(axis_info)

outer_mould_thickness = 20
inner_mould_thickness = 20

mould_top = axis_info['min'][depth_axis] + (axis_info['max'][depth_axis] - axis_info['min'][depth_axis]) * .7

def gen_box(axis_info, thickness, mould_top):
	return pymesh.generate_box_mesh([
		axis_info['min'][0] - thickness,
		axis_info['min'][1] - thickness,
		axis_info['min'][2] - thickness,
	],[
		axis_info['max'][0] + thickness,
		axis_info['max'][1] + thickness,
		mould_top,
	])

## TODO!! Remember draft angles!!
inner_mould = gen_box(axis_info, inner_mould_thickness, mould_top)
outer_mould = gen_box(axis_info, inner_mould_thickness + outer_mould_thickness, mould_top)

outer_mould = pymesh.boolean(outer_mould, inner_mould, operation="difference")
inner_mould = pymesh.boolean(inner_mould, mesh, operation="difference")

print("writing output")
pymesh.save_mesh("/models/next_gen_output_outer_mould.stl", outer_mould)
pymesh.save_mesh("/models/next_gen_output_inner_mould.stl", inner_mould)