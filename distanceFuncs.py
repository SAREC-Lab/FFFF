from math import radians, sin, cos, sqrt, atan2, sqrt

R = 6373.0
def getDistanceMeters(lat1, long1, lat2, long2):
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    long1 = radians(long1)
    long2 = radians(long2)

    dlong = long2 - long1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000
    return distance

def isCheckPoint(l_wypt, a_wypt1, a_wypt2):
    dist1 = round(distance(l_wypt[0], a_wypt1[0], l_wypt[1], a_wypt1[1]), 6)
    dist2 = round(distance(l_wypt[0], a_wypt2[0], l_wypt[1], a_wypt2[1]), 6)
    if dist2 > dist1:
        #print("current waypoint is a chkpt {} {}".format(dist1, dist2))
        return True
    #print("not a chkpt {} {}".format(dist1, dist2))
    return False

def distance(x1, x2, y1, y2):
    return sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
