import requests
import json
from leader_waypoints import wypts

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



server_addr = '127.0.0.1'
port = '5000'
r = requests.post('http://' + server_addr + ':' + port + '/createLeadDrone', data=json.dumps(wypts))
if r.status_code == 200:
    resp = json.loads(r.content)
else:
    print('Error: {} Response'.format(r.status_code))
    sys.exit(1)
waypoints=resp['waypoints']
print "Leader Waypoints::"
print waypoints
print '\n\n'

r = requests.get('http://' + server_addr + ':' + port + '/computeStraightLinePath')
if r.status_code == 200:
    resp = json.loads(r.content)
waypoints = resp['waypoints'] #dict(resp['waypoints'])
print 'Aux Waypoints::'
print waypoints
