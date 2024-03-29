import os
import time
import dronekit
import dronekit_sitl
import numpy as np
import nvector as nv
from pymavlink import mavutil


class DronekitHelpers:
    @staticmethod
    def start_sitl(sitl_instance, ardupath, home=(41.71544, -86.24284, 0)):
        home_str = ','.join(map(str, tuple(home) + (0,)))
        sitl_defaults = os.path.join(ardupath, 'Tools', 'autotest', 'default_params', 'copter.parm')
        sitl_args = ['-I{}'.format(sitl_instance), '--home', home_str, '--model', '+', '--defaults', sitl_defaults]

        sitl = dronekit_sitl.SITL(path=os.path.join(ardupath, 'build', 'sitl', 'bin', 'arducopter'))
        sitl.launch(sitl_args, await_ready=True)

        tcp, ip, port = sitl.connection_string().split(':')
        port = str(int(port) + sitl_instance * 10)
        conn_string = ':'.join([tcp, ip, port])

        return sitl, conn_string

    @staticmethod
    def connect_vehicle(connection_string, baud=57600):
        vehicle = dronekit.connect(connection_string, baud=baud)
        vehicle.wait_ready(timeout=120)

        while not vehicle.is_armable:
            time.sleep(1.0)

        return vehicle

    @staticmethod
    def set_mode(drone, trg_mode):
        cur_mode = drone.mode.name

        while trg_mode != cur_mode:
            drone.mode = dronekit.VehicleMode(trg_mode)
            time.sleep(1.0)
            cur_mode = drone.mode.name

    @staticmethod
    def arm(drone, armed=True):
        if drone.armed != armed:
            while not drone.is_armable:
                time.sleep(1.0)
            drone.armed = armed

            while drone.armed != armed:
                drone.armed = armed
                time.sleep(1.0)

    @staticmethod
    def takeoff(drone, alt):
        DronekitHelpers.set_mode(drone, 'GUIDED')
        DronekitHelpers.arm(drone)
        drone.simple_takeoff(alt)

        cur_alt = drone.location.global_relative_frame.alt

        while abs(cur_alt - alt) > 2:
            time.sleep(1.0)
            cur_alt = drone.location.global_relative_frame.alt


    @staticmethod
    def goto(drone, lat, lon, alt, speed=1):
        drone.simple_goto(dronekit.LocationGlobalRelative(lat, lon, alt))
        DronekitHelpers.set_speed(drone, speed)

        trg = Lla(lat, lon, alt)
        dist = trg.distance(DronekitHelpers.get_lla(drone))

        while dist > 2.0:
            time.sleep(1.0)
            dist = trg.distance(DronekitHelpers.get_lla(drone))


    @staticmethod
    def set_speed(drone, speed):
        msg = drone.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # command
            0,  # confirmation
            0,  # param 1
            speed,  # speed in metres/second
            0, 0, 0, 0, 0  # param 3 - 7
        )

        # send command to vehicle
        drone.send_mavlink(msg)
        drone.flush()

    @staticmethod
    def set_ned(drone, north, east, down, duration):
        msg = drone.message_factory.set_position_target_local_ned_encode(
            0,  # time_boot_ms (not used)
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
            0b0000111111000111,  # type_mask (only speeds enabled)
            0, 0, 0,  # x, y, z positions (not used)
            north, east, down,  # x, y, z velocity in m/s
            0, 0, 0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
        # send command to vehicle 
        for x in range(duration):
            # send command to vehicle
            drone.send_mavlink(msg)
            time.sleep(1.0)        

    @staticmethod
    def land(drone):
        DronekitHelpers.set_mode(drone, 'LAND')

    @staticmethod
    def get_lla(drone):
        pos = drone.location.global_relative_frame

        return Lla(pos.lat, pos.lon, pos.alt)

arr = np.array
SEMI_MAJOR = np.float64(6378137.0)
SEMI_MINOR = np.float64(6356752.31)

NV_A = SEMI_MAJOR
NV_F = 1 - (SEMI_MINOR / SEMI_MAJOR)


class Position(object):
    def __getitem__(self, item):
        return self.as_array()[item]

    def as_array(self, flat=True):
        a = self._as_array()
        if not flat:
            a = a.reshape(-1, 1)

        return a

    # noinspection PyTypeChecker
    def distance(self, other):
        p1 = self.to_pvector().as_array()
        p2 = other.to_pvector().as_array()

        resid = p1 - p2
        resid_sq = resid ** 2
        resid_sum_sq = resid_sq.sum()
        dist = np.sqrt(resid_sum_sq)

        return dist

    def coerce(self, other):
        if isinstance(other, Position):
            if isinstance(self, Lla):
                return other.to_lla()
            elif isinstance(self, Nvector):
                return other.to_nvector()
            else:
                return other.to_pvector()
        else:
            return other

    def n_E2R_EN(self):
        n_E = self.to_nvector().get_xyz(shape=(3, 1))
        R_EN = nv.n_E2R_EN(n_E)

        return R_EN

    def move_ned(self, north, east, down):
        p_EA_E = self.to_pvector().get_xyz()

        R_NE = self.n_E2R_EN()
        p_delta_E = R_NE.dot([north, east, down])

        p_EA_E_delta = p_EA_E + p_delta_E

        return self.coerce(Pvector(*p_EA_E_delta))

    def distance_ned(self, other):
        R_NE = self.n_E2R_EN().T

        p_AB_E = other.to_pvector().as_array() - self.to_pvector().as_array()
        p_AB_N = R_NE.dot(p_AB_E)

        return p_AB_N

    def __repr__(self):
        return '{}'.format(','.join(self.as_array().astype(str)))

    def __str__(self):
        return repr(self)

    # noinspection PyTypeChecker
    def __eq__(self, other):
        other_ = self.coerce(other)
        if isinstance(other_, self.__class__):
            return np.isclose(self.as_array(), other_.as_array()).all()
        return False

    def to_lla(self):
        raise NotImplementedError

    def to_nvector(self):
        raise NotImplementedError

    def to_pvector(self):
        raise NotImplementedError

    def _as_array(self):
        raise NotImplementedError


class Lla(Position):
    def __init__(self, latitude, longitude, altitude):
        self.lla = arr([latitude, longitude, altitude]).astype(np.float64)

    def get_latitude(self, as_rad=False):
        lat = self.lla[0]
        if as_rad:
            lat = np.deg2rad(lat)

        return lat

    def get_longitude(self, as_rad=False):
        lon = self.lla[1]
        if as_rad:
            lon = np.deg2rad(lon)

        return lon

    def get_altitude(self):
        return self.lla[-1]

    def to_nvector(self):
        lat = self.get_latitude(as_rad=True)
        lon = self.get_longitude(as_rad=True)
        alt = self.get_altitude()
        n_EB_E = nv.lat_lon2n_E(lat, lon)
        x, y, z = n_EB_E.ravel()

        return Nvector(x, y, z, -alt)

    def to_pvector(self):
        return self.to_nvector().to_pvector()

    def to_lla(self):
        return self

    def _as_array(self):
        return self.lla


class Nvector(Position):
    def __init__(self, x, y, z, depth):
        self.n_EB_E = arr([x, y, z]).astype(np.float64).reshape(-1, 1)
        self.depth = depth

    def get_x(self):
        return self.n_EB_E[0, 0]

    def get_y(self):
        return self.n_EB_E[1, 0]

    def get_z(self):
        return self.n_EB_E[2, 0]

    def get_xyz(self, shape=(3,)):
        return self.n_EB_E.ravel().reshape(shape)

    def get_depth(self):
        return self.depth

    def to_nvector(self):
        return self

    def to_pvector(self):
        x, y, z = nv.n_EB_E2p_EB_E(self.n_EB_E, depth=self.depth, a=NV_A, f=NV_F).ravel()

        return Pvector(x, y, z)

    def to_lla(self):
        lat, lon = nv.n_E2lat_lon(self.n_EB_E)

        return Lla(np.rad2deg(lat[0]), np.rad2deg(lon[0]), -self.depth)

    def _as_array(self):
        x, y, z = self.n_EB_E.ravel()
        return arr([x, y, z, self.depth])


class Pvector(Position):
    def __init__(self, x, y, z):
        self.p_EB_E = arr([x, y, z]).astype(np.float64).reshape(-1, 1)

    def __sub__(self, other):
        return self.p_EB_E.ravel() - other.p_EB_E.ravel()

    def get_x(self):
        return self.p_EB_E[0, 0]

    def get_y(self):
        return self.p_EB_E[1, 0]

    def get_z(self):
        return self.p_EB_E[2, 0]

    def get_xyz(self, shape=(3,)):
        xyz = self.p_EB_E.ravel().reshape(shape)
        return xyz

    def to_nvector(self):
        (x, y, z), depth = nv.p_EB_E2n_EB_E(self.p_EB_E, a=NV_A, f=NV_F)

        return Nvector(x, y, z, depth)

    def to_pvector(self):
        return self

    def to_lla(self):
        return self.to_nvector().to_lla()

    def _as_array(self):
        return self.p_EB_E.ravel()
