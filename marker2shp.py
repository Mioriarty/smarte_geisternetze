import xml.dom.minidom
import numpy as np
import geopandas as gpd
import shapely as shp
from shapely.geometry import Point
import pandas as pd
import utm
import math

file = xml.dom.minidom.parse("/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.xml")
#print(file.nodeName)
#print(file.firstChild.tagName)

Lon = file.getElementsByTagName("LongitudeDegrees")
Lat = file.getElementsByTagName("LatitudeDegrees")
Name = file.getElementsByTagName("Name")
Time = file.getElementsByTagName("RealTime")
Ping = file.getElementsByTagName("SonarElementIndex")
File = file.getElementsByTagName("Filename")
Channel = file.getElementsByTagName("SonarChannel")
Desc = file.getElementsByTagName("Description")

LON = []
LAT = []
NAME = []
TIME = []
PING = []
FILE = []
CHANNEL = []
DESC = []

# List comprehension
#for i in Lon:
#    #print(i.firstChild.nodeValue)
#    LON = pd.DataFrame(np.append(LON,float(i.firstChild.nodeValue)))



LON = [ np.append(LON,float(el.firstChild.nodeValue)) for el in Lon]
LAT = [ np.append(LAT,float(el.firstChild.nodeValue)) for el in Lat]
NAME = [ np.append(NAME,el.firstChild.nodeValue) for el in Name]
TIME = [ np.append(TIME,float(el.firstChild.nodeValue)) for el in Time]
PING = [ np.append(PING,int(el.firstChild.nodeValue)) for el in Ping]
FILE = [ np.append(FILE,el.firstChild.nodeValue) for el in File]
CHANNEL = [ np.append(CHANNEL,int(el.firstChild.nodeValue)) for el in Channel]
DESC = [ np.append(DESC,el.firstChild.nodeValue) for el in Desc]

#print(type(Lon))

df = np.c_[NAME,LON,LAT,TIME,PING,FILE,CHANNEL,DESC]
df = pd.DataFrame(df)

# add column names
df.columns = ['Name', 'Long', 'Lati','Time','Ping','File','Channel','Desc']

# combine lat and lon column to a shapely Point() object
df['geometry'] = df.apply(lambda x: Point((float(x.Long), float(x.Lati))), axis=1)

# convert to geo DF
df = gpd.GeoDataFrame(df, geometry='geometry')

# set coordinate system
gdf = df.set_crs(4326, allow_override=True)
#print(gdf.crs)
geo_df = gdf.to_crs({'init': 'epsg:32633'})
 

# write to shapefile
gdf.to_file('/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.shp', driver='ESRI Shapefile')
gdf.to_excel('/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.xlsx')

#print(geo_df)
