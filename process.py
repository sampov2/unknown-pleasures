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


def analyse_and_extract_path(path):
	points = path.getProperties()['points']

	minx =  100000
	maxx = -100000
	miny =  100000
	maxy = -100000
	avgy = 0

	i = 0
	points2d = []
	while i < len(points):
		x = points[i+0]
		y = points[i+1]

		minx = min(minx, x)
		maxx = max(maxx, x)
		miny = min(miny, y)
		maxy = max(maxy, y)

		avgy += y
		points2d.append((x,y))
		i += 2

	avgy /= len(points)/2
	return {
		'minx': minx,
		'maxx': maxx,
		'miny': miny,
		'maxy': maxy,
		'avgy': avgy,
		'points2d': points2d
	}

def load_and_extract(file):
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

	n = 0
	for i in group_of_groups.getContents():
		#print("processing object")
		path = find_right_path(i)
		if path != None:
			try:
				obj = analyse_and_extract_path(path)
				objects.append(obj)
				n += 1

			except Exception as e:
				print("unable to process polygon: {}".format(e))
		else:
			print("path not found")

	return objects

objects = load_and_extract(inputFile)

objects.sort(key=lambda o : o['maxy'])


zOffset = .5
height = 10
yExtension = 20

# Scaling would be nice, but we cannot do it individually...
s = 0.005
scaling_matrix = (
	(s, 0, 0, 0),
	(0, s, 0, 0),
	(0, 0, s, 0),
	(0, 0, 0, 1)
	);

minx =  100000
maxx = -100000
miny =  100000
maxy = -100000

for i in range(0, len(objects)):

	obj = objects[i]
	print('object #{}: miny = {}, height = {}'.format(i, obj['miny'], obj['maxy']-obj['miny']))
	points2d = obj['points2d']
	adjusted_points = []

	yThreshold = obj['maxy']-1
	for point in points2d:
		x = -point[0]
		y = point[1]

		minx = min(minx, x)
		maxx = max(maxx, x)
		miny = min(miny, y)
		maxy = max(maxy, y)

		if y > yThreshold:
			y += yExtension
		adjusted_points.append([x, y])

	polygon = Polygon(adjusted_points)
	try:
		mesh = trimesh.creation.extrude_polygon(polygon, height + zOffset*i)
	except:
		print('error with polygon:')
		print(adjusted_points)

	#mesh.apply_transform(scaling_matrix)
	print("writing output/{}.stl".format(i))
	mesh.export('output/{}.stl'.format(i))

base_box = Polygon(((minx,miny),(minx,maxy),(maxx, maxy), (maxx, miny)))
base_box_mesh = trimesh.creation.extrude_polygon(base_box, height-zOffset)
print("writing output/base_box.stl")
base_box_mesh.export('output/base_box.stl')

#mesh2.apply_scale(1.1)
#scene.export('output.stl', file_type='jpg')
#om.write_mesh('output.stl', mesh, binary=True)


## POST PROCESSING
# Scale, translate
# select all, join (A, CTRL-J)
# Edit mode -> mesh -> cleanup -> remove doubles