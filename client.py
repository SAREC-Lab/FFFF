import time
import requests
import json
import dronekit
from client_util import DronekitHelpers

# should probably be an argument
lead_drone = False

### FUNCTIONS ###

# stolen from example code
def connect_vehicle(connection_string, baud=57600):
	vehicle = dronekit.connect(connection_string, baud=baud)
	vehicle.wait_ready(timeout=120)
	
	while not vehicle.is_armable:
		time.sleep(1.0)

	return vehicle

# Register a callback: if the mode is ever switched to Loiter, this program will exit.
@drone.on_attribute('mode')
def handle_mode_change(_, name, msg):
    if msg.name == 'LOITER':
        drone.close()
        exit('Exiting: drone manually taken over.')

### MAIN ###
server_addr = '10.26.37.40'
port = '5000'

# Connect Drone 
connection_string = '/dev/ttyUSB0'
# ^Set this to the usb port where telem is plugged in (e.g., /dev/ttyUSB0)
drone = connect_vehicle(connection_string)

# connect to server
if (lead_drone):
	print('Starting client as Lead')
	print('Position: 0')
	mywaypoints={}
	r = requests.post(server_addr + ':' + port + '/createLeadDrone', data=json.dumps(mywaypoints))
	resp = json.loads(r.content)
	print(resp) # mostly checking this works
	waypoints=mywaypoints
else:
	print('Starting client as Auxiliary')
	r = requests.post(server_addr + ':' + port + '/createDrone')
	resp = json.loads(r.content)
	# add error checking
	print('Position: ' + resp['pos'])

	# wait for commands
	r = requests.get(server_addr + ':' + port + '/computePath')
	waypoints = json.loads(r.content)
	#print(waypoints)
	# should probably do some error checking :)

# i imagine it will be in this format
# {0 :
#	{lat :  4, long : 5, alt : 24, spd : 5 },
# 1 : ...

# convert to floats? tbd, use a map?

# Make sure that true location is being reported.
while drone.location.global_relative_frame.lat == 0:
    time.sleep(1.0)

print('STARTING UP')

alt = float(waypoints['0']['alt'])

home = drone.location.global_relative_frame

print('TAKING OFF')
DronekitHelpers.takeoff(drone, alt)

for wypt in waypoints:
	lat = float(waypoints[wypt]['lat'])
	lon = float(waypoints[wypt]['lon'])
	alt = float(waypoints[wypt]['alt'])
	spd = float(waypoints[wypt]['spd'])
	print('Flying to: {}, {}'.format(lat, lon))
	DronekitHelpers.goto(drone, lat, lon, alt, spd)

print('Path Complete')
#print('COMING HOME')
#DronekitHelpers.goto(drone, *home_lla.as_array(), speed=2)
print('Landing')
DronekitHelpers.land(drone)
