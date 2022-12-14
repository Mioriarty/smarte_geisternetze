import pyxtf
from xml.dom import minidom
from datetime import datetime
from xtf_png import xtf2png
import cv2
import numpy as np
import imageio
from Finding import Finding
from calc_lag import convert_coords
from pathlib import Path

class LaybackRecord:

    def __init__(self, filePath, defaultValue = 10):
        self.hasFile = filePath.exists()
        self.defaultValue = defaultValue
        self.laybackData = []

        if self.hasFile:
            doc = minidom.parse(str(filePath.absolute()))

            for element in doc.getElementsByTagName('event'):
                sonarIndex = int(element.getElementsByTagName('sonarindex')[0].firstChild.nodeValue)
                layback = max([ float(element.getElementsByTagName('x_offset')[0].firstChild.nodeValue), float(element.getElementsByTagName('y_offset')[0].firstChild.nodeValue), float(element.getElementsByTagName('z_offset')[0].firstChild.nodeValue) ])
                self.laybackData.append((sonarIndex, layback))
            
    
    def evaluate(self, pingNumber):
        if self.hasFile:
            lastDataPoint = 0
            lastDataPointsLayback = 0

            for (sonarIndex, layback) in self.laybackData:
                if sonarIndex < pingNumber and sonarIndex > lastDataPoint:
                    lastDataPoint = sonarIndex
                    lastDataPointsLayback = layback
            return lastDataPointsLayback
                    
        else:
            return self.defaultValue



def processFindings(findings, xtfPath, outputDirectory, gifSize = 300):
    (fh, p) = pyxtf.xtf_read(xtfPath)

    laybackPath = Path(Path(xtfPath).parent.parent, 'layback.xml')
    laybackRecord = LaybackRecord(laybackPath)

    # temp whole img
    tempPngFileName = "temp.png"
    xtf2png(xtfPath, tempPngFileName, False, False)
    wholeImg = cv2.imread(tempPngFileName, cv2.IMREAD_GRAYSCALE)
    

    root = minidom.Document()
    marker_list_xml = root.createElement('MarkerList')
    root.appendChild(marker_list_xml)

    pings = p[pyxtf.XTFHeaderType.sonar]
    
    
    for index, finding in enumerate(findings):
        markerName = "Mark" + str(index)

        createXMLMarker(pings[finding.getPingNumber()], finding, markerName, laybackRecord.evaluate(finding.getPingNumber()), root, marker_list_xml)
        createGif(finding, markerName, outputDirectory,  wholeImg, gifSize)
    
    with open(outputDirectory + "/marker.xml", "w") as f:
        f.write(root.toprettyxml(indent ="\t") )

def createXMLMarker(ping, finding, name,  layback, root_xml, marker_list_xml):
    marker = root_xml.createElement('Marker')

    range = ping.ping_chan_headers[0].SlantRange
    chanelWidth = ping.ping_chan_headers[0].NumSamples
    offset = finding.getGlobalPixelCoord(chanelWidth)[0] - chanelWidth
    offset = offset / chanelWidth * range

    latitude = ping.SensorYcoordinate # CALCS TODO
    longitude = ping.SensorXcoordinate # CALCS TODO
    heading = ping.Yaw

    latitude, longitude = convert_coords(longitude, latitude, heading, layback, offset)


    writeMarkerAttribute('Time', (ping.FixTimeHour * 60 +  ping.FixTimeMinute) * 60 + ping.FixTimeSecond, root_xml, marker)
    writeMarkerAttribute('RealTime', datetime(ping.Year, ping.Month, ping.Day, ping.Hour, ping.Minute, ping.Second ).timestamp(), root_xml, marker)
    writeMarkerAttribute('SonarElementIndex', ping.PingNumber, root_xml, marker)
    # writeMarkerAttribute('Range', '', root_xml, marker)
    writeMarkerAttribute('SonarChannel', finding.chanel, root_xml, marker)
    writeMarkerAttribute('Name', name, root_xml, marker)
    writeMarkerAttribute('Description', 'Automatically generated', root_xml, marker)
    writeMarkerAttribute('Filename', name + '.gif', root_xml, marker)
    # writeMarkerAttribute('HeightMeters', 'Automatically generated', root_xml, marker) Bild gr????e
    # writeMarkerAttribute('WidthMeters', 'Automatically generated', root_xml, marker)  Bild gr????e
    writeMarkerAttribute('LatitudeDegrees', latitude, root_xml, marker)
    writeMarkerAttribute('LongitudeDegrees',  longitude, root_xml, marker)
    # writeMarkerAttribute('COG', 'Automatically generated', root_xml, marker)          idk
    # writeMarkerAttribute('SOG', ping.SensorSpeed, root_xml, marker)                   Not realistic
    # writeMarkerAttribute('Altitude', 'Automatically generated', root_xml, marker)     Values in markars dont make sense
    # writeMarkerAttribute('Depth', 'Automatically generated', root_xml, marker)        Values in markars dont make sense
    # writeMarkerAttribute('Type', 'Automatically generated', root_xml, marker)         idk

    marker_list_xml.appendChild(marker)

def createGif(finding, markerName, outputDirectory, wholeImg, size):
    halfSize = size // 2
    chanelWidth = wholeImg.shape[0] // 2
    topLeft = [ max(0, min(finding.getGlobalPixelCoord(chanelWidth)[i] - halfSize, wholeImg.shape[i] - size)) for i in range(2) ]
    gifData = wholeImg[topLeft[0] : topLeft[0] + size, topLeft[1] : topLeft[1] + size]

    imageio.imwrite(outputDirectory + "/" + markerName + '.gif', gifData)

def writeMarkerAttribute(name, value, root_xml, marker_xml):
    attr = root_xml.createElement(name)
    val = root_xml.createTextNode(str(value))
    attr.appendChild(val)
    marker_xml.appendChild(attr)
    

if __name__ == '__main__':
    processFindings([Finding((10, 10), 1040, 'bot')], 'res/2019apr04_ecker_sued_10002.xtf', "xmlout")