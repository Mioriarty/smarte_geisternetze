import xml.dom.minidom
import numpy as np
import geopandas as gpd
import shapely as shp
from shapely.geometry import Point
import pandas as pd

file = xml.dom.minidom.parse("/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.xml")
print(file.nodeName)
print(file.firstChild.tagName)


file = xml.dom.minidom.parse("/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.xml")
print(file.nodeName)
print(file.firstChild.tagName)

Lon = file.getElementsByTagName("LongitudeDegrees")
Lat = file.getElementsByTagName("LatitudeDegrees")
Name = file.getElementsByTagName("Name")

LON = []
LAT = []
NAME = []


for i in Lon:
    #print(i.firstChild.nodeValue)
    LON = pd.DataFrame(np.append(LON,float(i.firstChild.nodeValue)))
    
for j in Lat:
    LAT = pd.DataFrame(np.append(LAT,float(j.firstChild.nodeValue)))
    #print(j.firstChild.nodeValue)
    
for k in Name:
    NAME = pd.DataFrame(np.append(NAME,k.firstChild.nodeValue))

df = np.c_[NAME,LON,LAT]
df = pd.DataFrame(df)

df.columns = ['Name', 'Lon', 'Lat']

print((df))

# combine lat and lon column to a shapely Point() object
df['geometry'] = df.apply(lambda x: Point((float(x.Lon), float(x.Lat))), axis=1)

df.crs= "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
df = gpd.GeoDataFrame(df, geometry='geometry')

df.to_file('/Volumes/RAKSHA/ORCC/SH/20190404ecker sued 1/marker.shp', driver='ESRI Shapefile')