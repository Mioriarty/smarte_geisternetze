import pyxtf

class Finding:
    def __init__(self, pixelCoord, imgNumber):
        self.pixelCoord = pixelCoord
        self.imgNumber = imgNumber
    
    def __init__(self, pixelCoord, imageFile):
        self.pixelCoord = pixelCoord
        imageFile = imageFile[:-4] if imageFile[-4:] == '.png' else imageFile
        splittedImageFile = imageFile.split('_')

        if(splittedImageFile[-1] == 'mask'):
            self.__init__(pixelCoord, int(splittedImageFile[-3]))
        else:
            self.__init__(pixelCoord, int(splittedImageFile[-2]))
    
    def getGlobalPixelCoord(self):
        return (self.pixelCoord[0], self.pixelCoord[1] + self.imgNumber)
    
def processFindings(findings, xtfPath):
    (fh, p) = pyxtf.xtf_read(xtfPath)
    # channels = [ pyxtf.concatenate_channel(p[pyxtf.XTFHeaderType.sonar], file_header=fh, channel=0, weighted=True),  
    #              pyxtf.concatenate_channel(p[pyxtf.XTFHeaderType.sonar], file_header=fh, channel=1, weighted=True) ]

    pings = p[pyxtf.XTFHeaderType.sonar]
    
    for finding in findings:
        handlePingOfFinding(pings[finding.getGlobalPixelCoord()[1]])


def handlePingOfFinding(ping):
    pass

if __name__ == '__main__':
    processFindings([], 'res\\2019apr04_ecker_sued_10002.xtf')