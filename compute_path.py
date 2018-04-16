#!/usr/bin/python

#LocationGlobalRelative(lat, lon, vehicles[vindex].location.global_relative_frame.alt)

import math
import json
import matplotlib.pyplot as plt
import pyclipper
from get_distance_meters import getDistanceMeters


def computePath(leader_waypoints, offset_id = 1):
    leader_waypoints = [[w[0], w[1]] for w in leader_waypoints]
    OFFSET_CONSTANT = 70000
    ARC_TOLERANCE = 2000
    scaled_waypoints = []
    print leader_waypoints
    for wypt in leader_waypoints:
        scaled_waypoints.append([pyclipper.scale_to_clipper(wypt[0]), pyclipper.scale_to_clipper(wypt[1])])

    pco = pyclipper.PyclipperOffset(0, ARC_TOLERANCE)
    pco.AddPath(scaled_waypoints, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    
    scaled_path = pco.Execute(offset_id * OFFSET_CONSTANT) #pyclipper.scale_to_clipper(OFFSET_CONSTANT))
    unscaled_path = []
    for wypt in scaled_path[0]:
        unscaled_path.append([pyclipper.scale_from_clipper(wypt[0]), pyclipper.scale_from_clipper(wypt[1])])
    
    print scaled_path


    # gaphing here for visual check of correctness
    leader_x = []
    leader_y = []

    for waypoint in leader_waypoints:
        leader_x.append(waypoint[0])
        leader_y.append(waypoint[1])


    follower1_x = []
    follower1_y = []
    for waypoint in unscaled_path:
        follower1_x.append(waypoint[0])
        follower1_y.append(waypoint[1])

    for i in range(0, len(leader_x)):
        plt.plot(leader_x[i:i+2], leader_y[i:i+2], 'ro-')

    for i in range(0, len(follower1_x)):
        plt.plot(follower1_x[i:i+2], follower1_y[i:i+2], 'go-')

    plt.show()

    total_distance = 0
    for i in range(len(unscaled_path) - 1):
        total_distance += getDistanceMeters(unscaled_path[i][0], unscaled_path[i][1], unscaled_path[i + 1][0], unscaled_path[i + 1][1])
    
    output = {
        'path': unscaled_path,
        'distance': total_distance
    }
    return json.dumps(output)

'''


leader_waypoints = ((180, 200), (260, 200), (260, 150), (180, 150))#, (180, 200))
#leader_waypoints = [(16.0,5.0),(14.0,6.0),(12.0,5.0),(11.0,2.0),(13.0,0.0),(15.0,1.0), (16.0, 5.0)]
leader_x = []
leader_y = []

for waypoint in leader_waypoints:
	leader_x.append(waypoint[0])
	leader_y.append(waypoint[1])

## ------------------- Scale Toward Center Point --------------------
#S = 1.3
#cx = sum(x) / float(len(x))
#cy = sum(y) / float(len(y))
#
#x_new = []
#y_new = []
#
#for waypoint in leader_waypoints:
#	x_new.append((  S * (waypoint[0] - cx) ) + cx)
#	y_new.append((  S * (waypoint[1] - cy) ) + cy)
## -------------------------------------------------------------------
	
# ------------------------ Using PyClipper ---------------------------
import pyclipper

pco = pyclipper.PyclipperOffset()
pco.AddPath(leader_waypoints, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
solution = pco.Execute(7.0)
print solution

follower1_x = []
follower1_y = []

follower2_x = []
follower2_y = []

for waypoint in solution[0]:
	follower1_x.append(waypoint[0])
	follower1_y.append(waypoint[1])

solution = pco.Execute(14.0)
for waypoint in solution[0]:
    follower2_x.append(waypoint[0])
    follower2_y.append(waypoint[1])

for i in range(0, len(leader_x)):
	plt.plot(leader_x[i:i+2], leader_y[i:i+2], 'ro-')
#	plt.plot(x_new[i:i+2], y_new[i:i+2], 'go-')
for i in range(0, len(follower1_x)):
	plt.plot(follower1_x[i:i+2], follower1_y[i:i+2], 'go-')

for i in range(0, len(follower2_x)):
    plt.plot(follower2_x[i:i+2], follower2_y[i:i+2], 'go-')

plt.ylabel('some numbers')
plt.show()
	
#print solution

#def rotate(origin, point, angle):
#	"""
#	Rotate a point counterclockwise by a given angle around a given origin.
#
#	The angle should be given in radians.
#	"""
#	angle = math.radians(angle)
#	
#	ox, oy = origin
#	px, py = point
#
#	qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
#	qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
#	return qx, qy
#	
#point = (3.0, 4.0)
#origin = (2.0, 2.0)
#
#print rotate(origin, point, 10)
'''

