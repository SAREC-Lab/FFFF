import time
import requests
import json
import sys
from leader_waypoints import wypts

#import dronekit
#from client_util import DronekitHelpers

lead_drone = False

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

# Register a callback: if the mode is ever switched to Loiter, this program will exit.
@drone.on_attribute('mode')
def handle_mode_change(_, name, msg):
    if msg.name == 'LOITER':
        drone.close()
        exit('Exiting: drone manually taken over.')


### MAIN ###
if __name__ == '__main__':
    # command line args
    if len(sys.argv) > 2:
        usage(1)
    if len(sys.argv) == 2:
        if sys.argv[1] == '-lead':
            lead_drone = True
        elif sys.argv[1] == '-h' or sys.argv[1] == '-help':
            usage(0)

    #server_addr = '10.26.37.40'
    server_addr = '127.0.0.1'
    port = '5000'

    # Connect Drone
    connection_string = '/dev/ttyUSB0'
    #connection_string = '/dev/ttyUSB0'
    # ^Set this to the usb port where telem is plugged in (e.g., /dev/ttyUSB0)
    drone = connect_vehicle(connection_string)

'''
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
        print(resp) # mostly checking this works
        waypoints=dict(wypts)
        print "THESE ARE THE WAYPOINTS"
        print waypoints
    else:
        print('Starting client as Auxiliary')
        r = requests.get('http://' + server_addr + ':' + port + '/computeStraightLinePath')
        if r.status_code == 200:
                resp = json.loads(r.content)
                print type(resp)
                waypoints = resp#['waypoints'] #dict(resp['waypoints'])
        else:
                print('Error: {} Response'.format(r.status_code))
                sys.exit(1)
'''
    # i imagine it will be in this format
    # {0 :
    #       {lat :  4, long : 5, alt : 24, spd : 5 },
    # 1 : ...


    # Make sure that true location is being reported.
    #while drone.location.global_relative_frame.lat == 0:
    #    time.sleep(1.0)

    print('STARTING UP')

    #alt = float(waypoints['0']['alt'])
    waypoints=dict(wypts)
    home = drone.location.global_relative_frame
    alt = 10
    print('TAKING OFF')
    DronekitHelpers.takeoff(drone, alt)
    print waypoints
    wypts = waypoints['waypoints']
    for wypt in wypts:
        lat = float(wypt[0])
        lon = float(wypt[1])
        #spd = float(wypt[2])
        spd = 5
        print('Flying to: {}, {}'.format(lat, lon))
        DronekitHelpers.goto(drone, lat, lon, alt, spd)

    print('Path Complete')
    #print('COMING HOME')
    #DronekitHelpers.goto(drone, *home_lla.as_array(), speed=2)
    print('Landing')
    #DronekitHelpers.land(drone)
