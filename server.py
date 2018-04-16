from flask import Flask, request
import requests
import json
from get_distance_meters import getDistanceMeters

from compute_path import computePath

app = Flask(__name__)

drone_list = []

class Drone(object):
    def __init__(self, number):
        self.number = number
        self.lead = not self.number # lead is true if number == 0
        self.path = None

lead_drone = Drone(0)

@app.route('/')
def helloWorld():
    return "Hello world"

@app.route('/createLeadDrone', methods=['POST'])
def createLeadDrone():
    print 'got request'
    waypoints = json.loads(request.data)
    lead_drone.path = waypoints['waypoints']
    drone_list.append(Drone(0))
    resp = {}
    total_distance = 0
    print waypoints
    for i in range(len(lead_drone.path) - 1):
        total_distance += getDistanceMeters(lead_drone.path[i][0], lead_drone.path[i][1], lead_drone.path[i + 1][0], lead_drone.path[i + 1][1])
    resp['distance'] = total_distance
    resp['waypoints'] = lead_drone.path
    resp['text'] = "Creating lead drone"
    resp['result'] = "Success"
    return json.dumps(resp)

@app.route('/computeStraightLinePath', methods=['GET'])
def returnComputedStraightLinePath():
    if request.method == 'GET':
        output = computePath(lead_drone.path, 1)
        return output
    else:
        pass

@app.route('/computeFlyingVPath:drone_id', methods=['GET'])
def returnComputedPath(drone_id):
    if request.method == 'GET':
        drone_list.append()
        output = computeFlyingVPath(drone_id, drone_list[0].path)
        return json.dumps(output)
    else:
        pass
