from flask import Flask, request
import requests
import json

app = Flask(__name__)

drone_list = []

class Drone(object):
    def __init__(self, number):
        self.number = number
        self.lead = not self.number # lead is true if number == 0
        self.path = None

@app.route('/')
def helloWorld():
    return "Hello world"

@app.route('/createLeadDrone' methods=['POST']):
def createLeadDrone():
    drone_list.append(Drone(0))
    return "Creating lead drone"

@app.route('/computeStraightLinePath:drone_id' methods=['GET']):
def returnComputedStraightLinePath(drone_id):
    if request.method == 'GET':
        drone_list.append()
        output = computeStraightLinePath(drone_id, drone_list[0].path)
        return output
    else:
        pass

@app.route('/computeFlyingVPath:drone_id' methods=['GET']):
def returnComputedPath(drone_id):
    if request.method == 'GET':
        drone_list.append()
        output = computeFlyingVPath(drone_id, drone_list[0].path)
        return output
    else:
        pass

@app.route()