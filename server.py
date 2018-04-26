from flask import Flask, request
import requests
import json
from distanceFuncs import getDistanceMeters, isCheckPoint

from compute_path import computePath

app = Flask(__name__)

drone_list = []

class Drone(object):
    def __init__(self, number):
        self.number = number
        self.lead = not self.number # lead is true if number == 0
        self.path = None
        self.path_distance = 0
        self.ready = False

lead_drone = Drone(0)

@app.route('/')
def helloWorld():
    return "Hello world"

@app.route('/createLeadDrone', methods=['POST'])
def createLeadDrone():
    # no duplicate lead drones
    for i, d in enumerate(drone_list):
        if d.number == 0:
            drone_list.pop(i)
    print("Creating lead drone")
    waypoints = json.loads(request.data)
    print waypoints
    lead_drone.path = waypoints['waypoints']
    drone_list.insert(0, Drone(0))
    resp = {}
    total_distance = 0
    print waypoints
    for i in range(len(lead_drone.path) - 1):
        total_distance += getDistanceMeters(lead_drone.path[i][0], lead_drone.path[i][1], lead_drone.path[i + 1][0], lead_drone.path[i + 1][1])
    resp['distance'] = total_distance
    resp['waypoints'] = lead_drone.path
    resp['text'] = "Creating lead drone"
    resp['result'] = "Success"
    lead_drone.path_distance = total_distance
    return json.dumps(resp)

@app.route('/computeStraightLinePath', methods=['GET'])
def returnComputedStraightLinePath():
    if request.method == 'GET':
        aux_drone = Drone(len(drone_list))
        print("Adding drone {}".format(aux_drone.number))
        drone_list.append(aux_drone)
        resp = computePath(lead_drone.path, 1)
        checkpoints=[]
        l_indx = 0
        for a_indx, wypt in enumerate(resp['waypoints'][1:]):
            #print(resp['waypoints'][a_indx])
            if isCheckPoint(lead_drone.path[l_indx], resp['waypoints'][a_indx], wypt):
                checkpoints.append(resp['waypoints'][a_indx])
                l_indx += 1
        resp['checkpoints'] = checkpoints
        resp['text'] = 'Generating path for auxillary drone'
        resp['result'] = 'Success'
        resp['id'] = aux_drone.number
        resp['lead_drone_distance'] = lead_drone.path_distance
        return json.dumps(resp)
    else:
        pass

@app.route('/continuePath', methods=['POST'])
def continuePath():
    d_id = int(json.loads(request.data)['drone_id'])
    #for d in drone_list:
     #   if d_id == d.number:
      #      d.ready = True
    drone_list[d_id].ready = True
    resp = {}
    for d in drone_list:
        if not d.ready:
            resp['continue'] = 1
            return json.dumps(resp)
    resp['continue'] = 0
    return json.dumps(resp)

@app.route('/passedCheckpoint', methods=['GET'])
def passedCheckpoints():
    for d in drone_list:
        d.ready = False
    resp = {'result' : 'success'}
    return json.dumps(resp)

@app.route('/pathComplete', methods=['POST'])
def pathComplete():
    d_id = int(json.loads(request.data)['drone_id'])
    for i, d in enumerate(drone_list):
        if d.number == d_id:
            drone_list.pop(i)
    resp = {'result' : 'success'}
    return json.dumps(resp)

@app.route('/computeFlyingVPath:drone_id', methods=['GET'])
def returnComputedPath(drone_id):
    if request.method == 'GET':
        drone_list.append()
        output = computeFlyingVPath(drone_id, drone_list[0].path)
        return json.dumps(output)
    else:
        pass
