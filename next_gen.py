#!/usr/bin/python2

## docker run -it --rm -v `pwd`:/models pymesh/pymesh python /models/next_gen.py 

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh;

print("loading meshes")
intersect = pymesh.load_mesh("/models/tilted/intersect2.stl")

meshes = []
for n in range(1,79): ## TODO: 79
	tmp = pymesh.load_mesh("/models/tilted/{}.stl".format(n))
	meshes.append(tmp)

print("combining swirls")
united_swirls = pymesh.CSGTree({"union": list(map(lambda x : { "mesh": x}, meshes))}).mesh

print("calculating intersect to clean up swirls")
result = pymesh.boolean(united_swirls, intersect, operation="intersection", engine="igl")

print("writing output")
pymesh.save_mesh("/models/next_gen_output.stl", result)
