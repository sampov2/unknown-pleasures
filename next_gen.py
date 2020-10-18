#!/usr/bin/python2

## docker run -it --rm -v `pwd`:/models pymesh/pymesh python /models/next_gen.py 

## https://pymesh.readthedocs.io/en/latest/mesh_boolean.html#boolean-interface

import pymesh;

meshes = []
for n in range(1,79): ## TODO: 79
	tmp = pymesh.load_mesh("/models/tilted/{}.stl".format(n))
	meshes.append(tmp)


p = list(map(lambda x : { "mesh": x}, meshes))

x = pymesh.CSGTree({"union": p})


pymesh.save_mesh("/models/next_gen_output.stl", x.mesh)