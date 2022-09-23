import utm 
import math
import numpy as np

def convert_coords(longitude,latitude,layback,heading):
    # Longitude, Latitude, Layback, Heading must be 1-d numpy arrays

    NORTH = []
    EAST = []
    ZONE = []
    LETTER = []
    LON_lag = []
    LAT_lag = []

    UTM = [ utm.from_latlon(la, lo) for la,lo in zip(latitude,longitude)  ]
    UTM = np.asarray(UTM)
    UTM = np.array(UTM.tolist())
    EAST = np.append(EAST,UTM[:,0])
    NORTH = np.append(NORTH,UTM[:,1])
    UTM_zone = np.append(ZONE,UTM[:,2])
    UTM_letter = np.append(LETTER,UTM[:,3])

    
    EAST_lag = [ea - l*math.sin(h) for l,h,ea in zip(layback,heading,EAST)]
    NORTH_lag = [no - l*math.cos(h) for l,h,no in zip(layback,heading,NORTH)]

    Deg_lag = [ utm.to_latlon(ea,no,z,l) for ea,no,z,l in zip(EAST_lag,NORTH_lag, UTM_zone, UTM_letter)]
    Deg_lag = np.asarray(Deg_lag)
    Deg_lag = np.array(Deg_lag.tolist())
    LON_lay = np.append(LON_lay, Deg_lag[:,1])
    LAT_lay = np.append(LAT_lay, Deg_lag[:,0])

    return LAT_lag, LON_lag


    