#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/next_gen.py 

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh;

print("loading meshes")
intersect = pymesh.load_mesh("/models/tilted/intersect2.stl")

base_box = pymesh.load_mesh("/models/tilted/base_box.stl")

meshes = [ base_box ]
for n in range(0,81):
	tmp = pymesh.load_mesh("/models/tilted/{}.stl".format(n))
	meshes.append(tmp)

print("combining squigglies + base_box")
united_swirls = pymesh.CSGTree({"union": list(map(lambda x : { "mesh": x}, meshes))}).mesh

print("calculating intersect to clean up squigglies")
result = pymesh.boolean(united_swirls, intersect, operation="intersection", engine="igl")

print("writing output")
pymesh.save_mesh("/models/unknown_pleasures_positive.stl", result)
