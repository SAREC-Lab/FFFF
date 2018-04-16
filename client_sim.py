import dronekit_sitl
import dronekit
import json
import argparse
import os
import threading
import time
import signal
import util
import logging
import requests
import json

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)

fh = logging.FileHandler('main.log', mode='w')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('| %(levelname)6s | %(funcName)8s:%(lineno)2d | %(message)s |')
fh.setFormatter(formatter)
_LOG.addHandler(fh)

lead_drone = False
DO_CONT = False

# make sure you change this so that it's correct for your system 
ARDUPATH = os.path.join('/', 'home', 'zjanicki', 'git', 'ardupilot')


def load_json(path2file):
    d = None
    try:
        with open(path2file) as f:
            d = json.load(f)
    except Exception as e:
        exit('Invalid path or malformed json file! ({})'.format(e))

    return d


def connect_vehicle(instance, home):
    home_ = tuple(home) + (0,)
    home_ = ','.join(map(str, home_))
    sitl_defaults = os.path.join(ARDUPATH, 'Tools', 'autotest', 'default_params', 'copter.parm')
    sitl_args = ['-I{}'.format(instance), '--home', home_, '--model', '+', '--defaults', sitl_defaults]
    sitl = dronekit_sitl.SITL(path=os.path.join(ARDUPATH, 'build', 'sitl', 'bin', 'arducopter'))
    sitl.launch(sitl_args, await_ready=True)

    tcp, ip, port = sitl.connection_string().split(':')
    port = str(int(port) + instance * 10)
    conn_string = ':'.join([tcp, ip, port])

    vehicle = dronekit.connect(conn_string)
    vehicle.wait_ready(timeout=120)

    return vehicle, sitl


def get_vehicle_id(i):
    return 'drone{}'.format(i)


def state_out_work(dronology, vehicles):
    while DO_CONT:
        for i, v in enumerate(vehicles):
            state = util.StateMessage.from_vehicle(v, get_vehicle_id(i))
            state_str = str(state)
            _LOG.info(state_str)
            dronology.send(state_str)

        time.sleep(1.0)


def main(path_to_config, ardupath=None):
    if ardupath is not None:
        global ARDUPATH
        ARDUPATH = ardupath
    
    global DO_CONT
    DO_CONT = True

    config = load_json(path_to_config)
    dronology = util.Connection()
    dronology.start()

    # A list of sitl instances.
    sitls = []
    # A list of drones. (dronekit.Vehicle)
    vehicles = []
    # A list of lists of lists (i.e., [ [ [lat0, lon0, alt0], ...] ...]
    # These are the waypoints each drone must go to!
    routes = []

    # Example:
    # vehicle0 = vehicles[0]
    # waypoints_for_vehicle0 = routes[0]
    # for waypoint in waypoints_for_vehicle0:
    #    lat, lon, alt = waypoint
    #    vehicle0.simple_goto(lat, lon, alt)

    # The above example obviously won't work... you'll need to write some code to figure out when the current waypoint
    # has been reached and it's time to go to the next waypoint.

    # Define the shutdown behavior
    def stop(*args):
        global DO_CONT
        DO_CONT = False
        w0.join()

        for v, sitl in zip(vehicles, sitls):
            v.close()
            sitl.stop()

        dronology.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    
    # Start up all the drones specified in the json configuration file
    for i, v_config in enumerate(config):
        home = v_config['start']
        vehicle, sitl = connect_vehicle(i, home)

        handshake = util.DroneHandshakeMessage.from_vehicle(vehicle, get_vehicle_id(i))
        dronology.send(str(handshake))

        sitls.append(sitl)
        vehicles.append(vehicle)
        routes.append(v_config['waypoints'])
        
    # Create a thread for sending the state of drones back to Dronology
    w0 = threading.Thread(target=state_out_work, args=(dronology, vehicles))
    # Start the thread.
    w0.start()

    server_addr = '127.0.0.1'
    port = '5000'

    # handle lead drone
    print("Starting Lead Drone")
    print("Pre-arm checks")
    while not vehicles[0].is_armable:
        print("Waiting for drone to initialize...")
        time.sleep(1)
	'''
    print("Arming motors")
    vehicles[0].mode = dronekit.VehicleMode("GUIDED")
    vehicles[0].armed = True

    while not vehicle.armed:
        print("Waiting to arm...")
        time.sleep(1)
	'''
    # Connect lead drone to server
    print("Connecting to server as Lead")
    wypts = routes[0]
    wypts = {'waypoints': wypts}
    r = requests.post('http://' + server_addr + ':' + port + '/createLeadDrone', data=json.dumps(wypts))
    if r.status_code == 200:
        resp = json.loads(r.content)
    else:
            print('Error: {} Response'.format(r.status_code))

    # handle second+ drones
    # random starting point from an example file
    home = [
      41.714867454724,
      -86.242300802635,
      0]
    vehicle, sitl = connect_vehicle(1, home)

    handshake = util.DroneHandshakeMessage.from_vehicle(vehicle, get_vehicle_id(1))
    dronology.send(str(handshake))

    sitls.append(sitl)
    vehicles.append(vehicle)

    print("Starting Auxillary Drone 1")
    print("Pre-arm checks")
    while not vehicles[1].is_armable:
        print("Waiting for drone to initialize...")
        time.sleep(1)

    print("Arming motors 0")
    vehicles[0].mode = dronekit.VehicleMode("GUIDED")
    vehicles[0].armed = True

    while not vehicles[0].armed:
        print("Waiting to arm...")
        time.sleep(1)

    print("Arming motors 1")
    print("Inside a loop")
    vehicles[1].mode = dronekit.VehicleMode("GUIDED")
    vehicles[1].armed = True

    while not vehicles[1].armed:
        print("Waiting to arm...")
        time.sleep(1)

    print("Connecting as aux drone 1")
    r = requests.get('http://' + server_addr + ':' + port + '/computeStraightLinePath')
    if r.status_code == 200:
    	resp = json.loads(r.content)
        wypts1 = dict(resp['waypoints'])
        routes.append(wypts1)
    else:
        print('Error: {} Response'.format(r.status_code))

    # setup should be complete...
    # takeoff
    counter = 0
    for vehicle in vehicles:
        starting_altitude = 10
        vehicle.simple_takeoff(starting_altitude) 
	# check to make sure we're at a safe height before raising the other ones
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= starting_altitude * 0.95:
                print("Reached target altitude for vehicle {}".format(counter))
                break
            time.sleep(1)
        counter += 1

    # lots of hardcoded stuff, need to change
    # base it off lead drone waypoints
    for i, wypts0 in enumerate(routes[0]):
        vehicles[0].simple_goto(wypts0, groundspeed=10)
        vehicles[1].simple_goto(routes[1][i*6], groundspeed=10)

        for j in range(1,5):
            vehicles[1].simple_goto(routes[1][j+i*6], groundspeed=10)

    # wait until ctrl c to exit
    while DO_CONT:
        time.sleep(5.0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path_to_config', type=str, help='the path to the drone configuration file.')
    ap.add_argument('--ardupath', type=str, default=ARDUPATH)
    args = ap.parse_args()
    main(args.path_to_config, ardupath=args.ardupath)
