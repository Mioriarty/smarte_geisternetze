import utm 
import math
import numpy as np

def convert_coords(la,lo,layback,heading,offset):

    UTM = utm.from_latlon(la, lo)
    UTM = np.asarray(UTM)
    EAST = np.float(UTM[0])
    NORTH = np.float(UTM[1])
    UTM_zone = np.int(UTM[2])
    UTM_letter = UTM[3]

    EAST_lag = np.float(EAST - layback*math.sin(heading))
    NORTH_lag = np.float(NORTH - layback*math.cos(heading))

    # calculate difference for x,y, components of original point and layback point
    # and flip vector to make it point in forward/ship movement direction (*(-1))
    DIFF_E = EAST - EAST_lag
    DIFF_N = NORTH - NORTH_lag
    DIFF = (np.array([DIFF_E, DIFF_N]))*(-1)

    # rotate DIFF vector in 90° to get offset in x-direction
    rot_mat = np.matrix([[0,1],[-1,0]])
    ROT = np.dot(rot_mat,DIFF)

    # normalise rotated DIFF vector 
    ROT = ROT/np.linalg.norm(ROT)*offset

    ROT_E = EAST_lag + ROT[0,0]
    ROT_N = NORTH_lag + ROT[0,1]

    Deg_lag = utm.to_latlon(ROT_E, ROT_N, UTM_zone, UTM_letter)
    Deg_lag = np.asarray(Deg_lag)
    Deg_lag = np.array(Deg_lag.tolist())
    LON_lag = Deg_lag[0]
    LAT_lag = Deg_lag[1]


    return LAT_lag, LON_lag, ROT_E

a = convert_coords(54.23,9.78,10,30,3)
print(a)
    