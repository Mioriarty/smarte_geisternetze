class Finding:
    def __init__(self, pixelCoord, imgNumber, chanel):
        self.pixelCoord = pixelCoord
        self.imgNumber = imgNumber
        self.chanel = chanel if isinstance(chanel, int) else (1 if chanel == 'top' else 2)
    
    @staticmethod
    def fromFileName(pixelCoord, imageFile):
        imageFile = imageFile[:-4] if imageFile[-4:] == '.png' else imageFile
        splittedImageFile = imageFile.split('_')

        if(splittedImageFile[-1] == 'mask'):
            return Finding(pixelCoord, int(splittedImageFile[-3]), splittedImageFile[-2])
        else:
            return Finding(pixelCoord, int(splittedImageFile[-2]), splittedImageFile[-1])
    
    def getPingNumber(self):
        return self.pixelCoord[1] + self.imgNumber
    
    def getGlobalPixelCoord(self, chanelWidth):
        if self.chanel == 1:
            return (self.pixelCoord[0], self.getPingNumber())
        else:
            return (self.pixelCoord[0] + chanelWidth, self.getPingNumber())