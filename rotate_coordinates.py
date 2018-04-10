#!/usr/bin/python

#LocationGlobalRelative(lat, lon, vehicles[vindex].location.global_relative_frame.alt)

import math
import matplotlib.pyplot as plt

leader_waypoints = [(6.0,5.0),(4.0,6.0),(2.0,5.0),(1.0,2.0),(3.0,0.0),(5.0,1.0)]
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
solution = pco.Execute(1.1)

follower1_x = []
follower1_y = []

for waypoint in solution[0]:
	follower1_x.append(waypoint[0])
	follower1_y.append(waypoint[1])

for i in range(0, len(leader_x)):
	plt.plot(leader_x[i:i+2], leader_y[i:i+2], 'ro-')
#	plt.plot(x_new[i:i+2], y_new[i:i+2], 'go-')
for i in range(0, len(follower1_x)):
	plt.plot(follower1_x[i:i+2], follower1_y[i:i+2], 'go-')

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

