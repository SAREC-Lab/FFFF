from flask import Flask, request
import requests
import json

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
    return "Creating lead drone"

@app.route('/computeStraightLinePath', methods=['GET'])
def returnComputedStraightLinePath():
    if request.method == 'GET':
        output = computePath(lead_drone.path, 1)
        return json.dumps({'path': output})
    else:
        pass

@app.route('/computeFlyingVPath:drone_id', methods=['GET'])
def returnComputedPath(drone_id):
    if request.method == 'GET':
        drone_list.append()
        output = computeFlyingVPath(drone_id, drone_list[0].path)
        return output
    else:
        pass