#!/usr/bin/python2

import trimesh 
from shapely.geometry import Polygon, Point
import shapely
from svglib.svglib import svg2rlg
from reportlab.graphics import shapes;

#inputFile = 'original/single-wave.svg'
#inputFile = 'original/two-waves.svg'
inputFile = 'original/drawing-3.svg'


def get_methods(object, spacing=20): 
  methodList = [] 
  for method_name in dir(object): 
    try: 
        if callable(getattr(object, method_name)): 
            methodList.append(str(method_name)) 
    except: 
        methodList.append(str(method_name)) 
  processFunc = (lambda s: ' '.join(s.split())) or (lambda s: s) 
  for method in methodList: 
    try: 
        print(str(method.ljust(spacing)) + ' ' + 
              processFunc(str(getattr(object, method).__doc__)[0:90])) 
    except: 
        print(method.ljust(spacing) + ' ' + ' getattr() failed') 

def show_object_tree(obj,n=0,depth=0):
	print('{}- {} {}'.format(' '*depth, obj, n))
	subCount = 0
	if hasattr(obj, 'getContents'):
		x = 0
		for i in obj.getContents():
			subCount += show_object_tree(i,x,depth+1)
			x += 1
	else:
		subCount = 1
	if depth == 1:
		print('{}- {}'.format(' '*(depth+1), subCount))
	return subCount


def find_right_path(obj):
	if isinstance(obj, shapes.Path):
		if obj.getProperties()['fillColor'] != None:
			return obj
	elif isinstance(obj, shapes.Polygon):
		print("skipping Polygon")
	elif isinstance(obj, shapes.PolyLine):
		print("skipping PolyLine")
	else:
		for i in obj.getContents():
			ret = find_right_path(i)
			if ret != None:
				return ret
	return None

def extrude_svg_path(path, height = 30, zOffset = 0, xOffset = 0, yOffset = 0):
	points2d = path.getProperties()['points']

	points3d = []
	i = 0
	print("offsets (x, y, z) = ({}, {}, {})".format(xOffset, yOffset, zOffset))
	while i < len(points2d):
		points3d.append(
			(points2d[i+0]+ xOffset, 
			 points2d[i+1] + yOffset,
			 0))
		i += 2

	polygon = Polygon(points3d)
	return trimesh.creation.extrude_polygon(polygon, height+zOffset)

def load_and_extrude(file, height):
	drawing = svg2rlg(inputFile)

	assert len(drawing.getContents()) == 1

	main_group = drawing.getContents()[0]

	assert len(main_group.getContents()) == 1

	group_of_groups = main_group
	while len(group_of_groups.getContents()) == 1:
		print('deeper')
		group_of_groups = group_of_groups.getContents()[0]

	print len(group_of_groups.getContents())
	#group1 = main_group.getContents()[0]

	#print('group 1 length {}'.format(len(group1.getContents())))

	#assert len(group1.getContents()) == 1

	objects = []

	zOffset = 5
	height = 10

	n = 0
	for i in group_of_groups.getContents():
		print("processing object")
		path = find_right_path(i)
		if path != None:
			try:
				#for x in range(0,10):
					print("extrude")
					obj = extrude_svg_path(path, height, 
						zOffset=zOffset*n, xOffset=zOffset*n*0, yOffset=zOffset*n*1)
					objects.append(obj)
					n += 1

			except:
				print("unable to process polygon")
		else:
			print("path not found")

	return objects

objects = load_and_extrude(inputFile, 30)

#foo = (objects[0], objects[1], objects[2])
foo = objects[0:6] # works okay

#foo = objects[5:8] # shows only two..
#foo = objects[6:8] # shows two..
#foo = objects[6:9] # shows two..
#foo = objects[6:10] # shows two..

#foo = objects

#foo = objects[1:7] # horribly broken

mesh = trimesh.boolean.union(foo, 'blender')
#mesh.fix_normals()

mesh.vertices -= mesh.center_mass
#mesh = mesh.scaled(0.05)

s = 0.005
scaling_matrix = (
	(s, 0, 0, 0),
	(0, s, 0, 0),
	(0, 0, s, 0),
	(0, 0, 0, 1)
	);

mesh.apply_transform(scaling_matrix)
print("writing output.stl")
mesh.export('output.stl')


#mesh2.apply_scale(1.1)
#scene.export('output.stl', file_type='jpg')
#om.write_mesh('output.stl', mesh, binary=True)
