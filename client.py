import time
import requests
import json
import sys
from leader_waypoints import wypts

import dronekit
from client_utils import DronekitHelpers

lead_drone = False
BASE_SPEED = 5

### FUNCTIONS ###

def usage(status=0):
        print('Usage: ./client.py\n\t-lead\tSpecifies this instance as lead drone')
        sys.exit(status)

# stolen from example code
def connect_vehicle(connection_string, baud=57600):
    vehicle = dronekit.connect(connection_string, baud=baud)
    vehicle.wait_ready(timeout=120)
    
    while not vehicle.is_armable:
        time.sleep(1.0)

    return vehicle


connection_string = sys.argv[2]
drone = DronekitHelpers.connect_vehicle(connection_string)

# Register a callback: if the mode is ever switched to Loiter, this program will exit.
@drone.on_attribute('mode')
def handle_mode_change(_, name, msg):
    if msg.name == 'LOITER':
        drone.close()
        exit('Exiting: drone manually taken over.')


### MAIN ###
if __name__ == '__main__':
    # command line args
    '''
    if len(sys.argv) > 2:
        usage(1)
    if len(sys.argv) == 2:
        if sys.argv[1] == '-lead':
            lead_drone = True
        elif sys.argv[1] == '-h' or sys.argv[1] == '-help':
            usage(0)
    connection_string = sys.argv[2]
    '''
    if sys.argv[1] == '-lead':
        lead_drone = True
    

    server_addr = '165.227.198.38'
    #server_addr = '127.0.0.1'
    port = '5000'

    
    # connect to server
    if (lead_drone):
        print('Starting client as Lead')
        print('Position: 0')
        r = requests.post('http://' + server_addr + ':' + port + '/createLeadDrone', data=json.dumps(wypts))
        if r.status_code == 200:
            resp = json.loads(r.content)
        else:
            print('Error: {} Response'.format(r.status_code))
            sys.exit(1)
        waypoints = resp['waypoints']
    
    else:
        print('Starting client as Auxiliary')
        r = requests.get('http://' + server_addr + ':' + port + '/computeStraightLinePath')
        if r.status_code == 200:
            resp = json.loads(r.content)
            waypoints = resp['waypoints'] 
        else:
            print('Error: {} Response'.format(r.status_code))
            sys.exit(1)


    # Make sure that true location is being reported.
    #while drone.location.global_relative_frame.lat == 0:
    #    time.sleep(1.0)

    print('STARTING UP')

    #waypoints=dict(wypts)
    home = drone.location.global_relative_frame
    if lead_drone:
        alt = 10
    else:
        alt = 8
    print('TAKING OFF')
    DronekitHelpers.takeoff(drone, alt)
    print waypoints
    for i, wypt in enumerate(waypoints):
        lat = float(wypt[0])
        lon = float(wypt[1])
        if lead_drone:
            spd = BASE_SPEED
        else:
            spd = BASE_SPEED * (resp['lead_drone_distance'] / resp['distance']) 
        print('Flying to: {}, {}'.format(lat, lon))
        DronekitHelpers.goto(drone, lat, lon, alt, spd)
        if i == 0:
            command = raw_input('press any key and enter to go')

    print('Path Complete')
    #print('COMING HOME')
    #DronekitHelpers.goto(drone, *home_lla.as_array(), speed=2)
    print('Landing')
    DronekitHelpers.land(drone)
