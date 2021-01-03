#!/usr/bin/python2

## docker run -it --rm -v $PWD:/models pymesh-unknown-pleasures python /models/tilt_process.py


import trimesh 
import math
from shapely.geometry import Polygon, Point
import shapely
from svglib.svglib import svg2rlg
from reportlab.graphics import shapes;
from transforms3d.euler import euler2mat;

import numpy as np
from scipy import interpolate

#inputFile = 'original/single-wave.svg'
#inputFile = 'original/two-waves.svg'
inputFile = '/models/original/drawing-3.svg'

outputDir = '/models/tilted/';

## Try out both rotate and tilt!

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


def find_right_path(obj, n):
	if isinstance(obj, shapes.Path):
		if obj.getProperties()['fillColor'] != None:
			return obj
	elif isinstance(obj, shapes.Polygon):
		if obj.getProperties()['fillColor'] != None:
			return obj
		print("skipping Polygon #{}".format(n))
	elif isinstance(obj, shapes.PolyLine):
		print("skipping PolyLine #{}".format(n))
	else:
		for i in obj.getContents():
			ret = find_right_path(i,n )
			if ret != None:
				return ret
	return None

def create_intersect_face(minx, miny, maxx, maxy):
	rSide = 0.5
	rMid = 0.7
	width  = maxx - minx
	height = (maxy - miny) / 2

	side = width * rSide / 2
	mid = width * rMid / 2
	#mid = (width-side) * (1-r) / 2
	h = height

	xoffset = -(maxx-minx)/2 + maxx
	yoffset = -5

	ctr = np.array( [
			(xoffset-(side+mid), yoffset-4*h), 
			(xoffset-(side+mid), yoffset-3*h), 
			(xoffset-(side+mid), yoffset+1*h),
			(xoffset-(mid), yoffset+1*h),
			(xoffset-(mid), yoffset+5.5*h),
			(xoffset+(mid), yoffset+5.5*h), 
			(xoffset+(mid), yoffset+1*h),
			(xoffset+(side+mid), yoffset+1*h), 
			(xoffset+(side+mid), yoffset-3*h),
			(xoffset+(side+mid), yoffset-4*h)])


	print('minx: {}, maxx: {}'.format(minx, maxx))
	print('ctr[0][0]: {}'.format(ctr[0][0]))
	print('ctr[9][0]: {}'.format(ctr[9][0]))

	x=ctr[:,0]
	y=ctr[:,1]

	print(x)
	print(y)

	l=len(x)  

	t=np.linspace(0,1,l-2,endpoint=True)
	t=np.append([0,0,0],t)
	t=np.append(t,[1,1,1])

	tck=[t,[x,y],3]
	u3=np.linspace(0,1,(max(l*2,70)),endpoint=True)
	out = interpolate.splev(u3,tck)

	firstx = ctr[0][0]
	firsty = ctr[0][1]

	out[0] = np.append(out[0], firstx)
	out[1] = np.append(out[1], firsty)

	return [ (out[0][i], out[1][i]) for i in range(len(out[0]))]
	


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

		# flip x
		x = -x

		## TODO: need a better method to detect the "lower
		#        straight edges" of the polys
		# If you look at y coordinates as a histogram, there
		# should be a valley next to the edge coordinates.
		# On the edge, there should be at least two points, 
		# probably more. Next to this there should be a valley
		# (though not necessarily)
		#
		# 
		minx = min(minx, x)
		maxx = max(maxx, x)
		miny = min(miny, y)
		maxy = max(maxy, y)

		avgy += y
		points2d.append([x,y])
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
	drawing = svg2rlg(file)

	assert len(drawing.getContents()) == 1

	main_group = drawing.getContents()[0]

	assert len(main_group.getContents()) == 1

	group_of_groups = main_group
	while len(group_of_groups.getContents()) == 1:
		group_of_groups = group_of_groups.getContents()[0]

	#print(len(group_of_groups.getContents()))
	#group1 = main_group.getContents()[0]

	#print('group 1 length {}'.format(len(group1.getContents())))

	#assert len(group1.getContents()) == 1

	objects = []

	n = 0
	for i in group_of_groups.getContents():
		#print("processing object")
		path = find_right_path(i, n)
		if path != None:
			try:
				obj = analyse_and_extract_path(path)
				objects.append(obj)
				n += 1

			except Exception as e:
				print("unable to process polygon #{}: {}".format(n,e))
		else:
			print("path not found")

	return objects

objects = load_and_extract(inputFile)

objects.sort(key=lambda o : o['maxy'])

xHalfway = sum(map(lambda o : o['minx'] + o ['maxx'], objects)) / (len(objects)*2)
minMinY = min(map(lambda o : o['miny'], objects))
maxMinY = max(map(lambda o : o['miny'], objects))

print('xHalfway = {}'.format(xHalfway))
print('xmin range = {} .. {}'.format(minMinY, maxMinY))

yStep = (maxMinY - minMinY) / len(objects)
yPos = minMinY

height = 80
yExtension = 20

# Scaling would be nice, but we cannot do it individually...
def rotation_matrix_3d(deg):
	rot = deg * math.pi / 180
	return (
		(1, 0,             0,              0),
		(0, math.cos(rot), -math.sin(rot), 0),
		(0, math.sin(rot), math.cos(rot),  0),
		(0, 0,             0,              1)
		);

rotation_matrix = rotation_matrix_3d(15)


#zz = euler2mat(rot, 0, 0)
#print(zz)

minx =  100000
maxx = -100000
miny =  100000
maxy = -100000

leftMaxX = -100000
rightMinX = 100000

def clean_bottom_and_extend(points2d, yExtension):
	tmp = Polygon(points2d)
	tmp.centroid
	#print('centroid: {}'.format(tmp.centroid))

	points_by_distance_to_centroid = []
	for point in points2d:
		if point[1] > tmp.centroid.y:
			p = Point(point)
			points_by_distance_to_centroid.append({
				'point': point,
				'idx': points2d.index(point),
				'distance': tmp.centroid.distance(p)
			})

	points_by_distance_to_centroid.sort(key=lambda o : -o['distance'])
	corners = [
		next(o for o in points_by_distance_to_centroid if o['point'][0] < tmp.centroid.x),
		next(o for o in points_by_distance_to_centroid if o['point'][0] > tmp.centroid.x)
	]

	#print('corners {}'.format(corners))
	#print('points {}'.format(len(points2d)))
	y = max(corners[0]['point'][1], corners[1]['point'][1])

	# Figure out points between the corners
	left_idx  = min(corners[0]['idx'], corners[1]['idx'])
	right_idx = max(corners[0]['idx'], corners[1]['idx'])
	all_idxs = set(range(0,len(points2d)))
	within_idx = set(range(left_idx, right_idx+1))
	outside_idx = all_idxs - within_idx # + set([left_idx, right_idx])

	#print('points {}, len(within) {}, len(outside)'.format(len(points2d), len(within_idx), len(outside_idx)))

	# The switch y value for all points in the "shortest path"
	if len(within_idx) < len(outside_idx):
		for i in within_idx:
			points2d[i][1] = y + yExtension
	else:
		for i in outside_idx:
			points2d[i][1] = y + yExtension
		points2d[left_idx][1] = y + yExtension
		points2d[right_idx][1] = y + yExtension

	#points2d[corners[0]['idx']][1] = y + yExtension
	#points2d[corners[1]['idx']][1] = y + yExtension

	return points2d

for i in range(0, len(objects)):

	obj = objects[i]
	#print('object #{}: miny = {}, height = {}'.format(i, obj['miny'], obj['maxy']-obj['miny']))
	#print('#{}, maxy = {}'.format(i, obj['maxy']))
	points2d = obj['points2d']
	adjusted_points = []

	## This stretching bugs out
	yThreshold = obj['maxy']-1
	points2d = clean_bottom_and_extend(points2d, yExtension)
	for point in points2d:
		x = -point[0]
		y = point[1]
		adjusted_points.append([x, y])
	polygon = Polygon(adjusted_points)

	try:
		mesh = trimesh.creation.extrude_polygon(polygon.simplify(.5, preserve_topology=True), height)
		for point in points2d:
			x = -point[0]
			y = point[1]

			minx = min(minx, x)
			maxx = max(maxx, x)
			miny = min(miny, y)
			maxy = max(maxy, y)

	except Exception as e:
		print('!!! error with polygon #{}: {}'.format(i,e))
		print(adjusted_points)
		continue

	print('#{}, obj["maxy"] = {}, maxy = {}'.format(i, round(obj['maxy'],2), round(maxy, 2)))

	translate_center = ((1, 0, 0, 0),
						(0, 1, 0, -yPos),
						(0, 0, 1, 0),
						(0, 0, 0, 1))
	translate_back =   ((1, 0, 0, 0),
						(0, 1, 0, yPos),
						(0, 0, 1, 0),
						(0, 0, 0, 1))

	yPos = yPos + yStep

	mesh.apply_transform(translate_center)
	mesh.apply_transform(rotation_matrix)
	mesh.apply_transform(translate_back)
	#print("writing {}/{}.stl".format(outputDir, i))
	mesh.export('{}/{}.stl'.format(outputDir, i))

def translate_down_3d(n):
	return ((1, 0, 0, 0),
		  	(0, 1, 0, 0),
			(0, 0, 1, n),
		  	(0, 0, 0, 1))

def write_box(minx, miny, maxx, maxy, height, yOffset, filename):
	box = Polygon(((minx,miny),(minx,maxy),(maxx, maxy), (maxx, miny)))
	mesh = trimesh.creation.extrude_polygon(box, height)
	mesh.apply_transform(translate_down_3d(yOffset))
	print("writing {}/{}.stl".format(outputDir, filename))
	mesh.export('{}/{}.stl'.format(outputDir, filename))

write_box(minx,miny,maxx,maxy, height, height/3, 'base_box')

write_box(minx+5,miny,maxx-5,maxy, height*5, -height*2, 'intersect2');


print('height {}'.format(height))
print('miny {}'.format(miny))
print('maxy {}'.format(maxy))
intersect_face = create_intersect_face(minx, 0, maxx, height)
intersect_poly = Polygon(intersect_face)
intersect_mesh = trimesh.creation.extrude_polygon(intersect_poly, (maxy - miny)+height)

intersect_mesh.apply_transform(translate_down_3d(miny-height))
intersect_mesh.apply_transform(rotation_matrix_3d(-90))


print("writing {}/intersect.stl".format(outputDir))
intersect_mesh.export('{}/intersect.stl'.format(outputDir))


#mesh2.apply_scale(1.1)
#scene.export('output.stl', file_type='jpg')
#om.write_mesh('output.stl', mesh, binary=True)


## POST PROCESSING
# Scale, translate
# select all, join (A, CTRL-J)
# Edit mode -> mesh -> cleanup -> remove doubles