import requests
import json

host = '127.0.0.1'
port = '5000'

waypoints = json.dumps(
    {"waypoints": [
        [
          41.71462,
          -86.24179,
          10
        ],
        [
          41.71462,
          -86.24239,
          10
        ],
        [
          41.71498,
          -86.24239,
          10
        ],
        [
          41.71498,
          -86.24179,
          10
        ],
        [
          41.71462,
          -86.24179,
          10
        ]
    ]})



r = requests.post('http://127.0.0.1:5000/createLeadDrone', data = waypoints)
print r.text

r = requests.get('http://127.0.0.1:5000/computeStraightLinePath')
print r.text