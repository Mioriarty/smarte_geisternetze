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

    DIFF_E = EAST - EAST_lag
    DIFF_N = NORTH-NORTH_lag
    DIFF = np.array([DIFF_E, DIFF_N])
    rot_mat = np.matrix([[0,1],[-1,0]])
    ROT = np.dot(rot_mat,DIFF)
    print(ROT)
    ROT = ROT/np.linalg.norm(ROT)*offset
    print(ROT[0,0])

    ROT_E = EAST_lag + ROT[0,0]
    ROT_N = NORTH_lag + ROT[0,1]

    Deg_lag = utm.to_latlon(ROT_E, ROT_N, UTM_zone, UTM_letter)
    Deg_lag = np.asarray(Deg_lag)
    Deg_lag = np.array(Deg_lag.tolist())
    LON_lag = Deg_lag[1]
    LAT_lag = Deg_lag[0]


    return LAT_lag, LON_lag
    