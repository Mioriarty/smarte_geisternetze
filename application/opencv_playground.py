from concurrent.futures import process
import glob
import cv2
import numpy as np
import multiprocessing
from Finding import Finding

def loopOverImages(dir):
    print(dir)

    processes = 8
    sonarTopImgs = glob.glob("{}*top.png".format(dir))
    sonarBotImgs = glob.glob("{}*bot.png".format(dir))

    print("Starting filtering...")
    with multiprocessing.Pool(processes = processes) as pool:
            findingsTop = pool.starmap(imgFiltering, [ (sonarImage, glob.glob("{}_mask.png".format(sonarImage[: - 4]))[0]) for sonarImage in sonarTopImgs ])
            findingsBot = pool.starmap(imgFiltering, [ (sonarImage, glob.glob("{}_mask.png".format(sonarImage[: - 4]))[0]) for sonarImage in sonarBotImgs ])  

    findings = [finding for finding in findingsBot + findingsTop if finding != None ]

    return findings

def imgFiltering(url, maskUrl):
    img = cv2.imread(url)
    imgMask = cv2.imread(maskUrl)
    imgMask = cv2.cvtColor(imgMask, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    

    clahe = cv2.createCLAHE(clipLimit = 1)
    cl1 = clahe.apply(imgGray)

    imgMask = resize(imgMask)
    cl1 = resize(cl1)

    cl1NlMeanDN = cv2.fastNlMeansDenoising(cl1, dst=True, h=7, searchWindowSize=55)

    image = detectEdgesAndDisplay(imgMask, cl1NlMeanDN)

    return getFinding(image, url)

def getFinding(image, url):
    whitePixels = cv2.findNonZero(image)
    if whitePixels is None:
        return
    
    finding = Finding.fromFileName(whitePixels[0][0], url)

    return finding

def display(windowName, images):
    cv2.imshow(windowName, images)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize(image):
    scale_percent = 40 # percent of original size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

def detectEdgesAndDisplay(imgMask, cl1):
    # Canny Edge Detection good values for unedited images th1=75 th2=225
    cl1Edges = cv2.Canny(image=cl1, threshold1=75, threshold2=225)
    cl1Edges = cv2.bitwise_and(cl1Edges, cl1Edges, mask=imgMask)
    cl1Edges = cv2.morphologyEx(cl1Edges, cv2.MORPH_CLOSE, kernel=np.ones((2,2), np.uint8))
    cl1Edges = cv2.dilate(cl1Edges, kernel=np.ones((3,3), np.uint8), iterations=1)
    contours, hierachy = cv2.findContours(cl1Edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contourImage = np.zeros((cl1.shape[0], cl1.shape[1]), dtype=np.uint8)

    for i in range(len(contours)):
        if(isContourLine(contours[i])):
            cv2.drawContours(contourImage, contours, i, (255, 255, 255), 2, cv2.LINE_4, hierachy, 0)

    return contourImage

def isContourLine(contour):
    hull = cv2.convexHull(contour)
    hullArea = cv2.contourArea(hull)
    hullPerimeter = cv2.arcLength(hull, True)

    _, radius = cv2.minEnclosingCircle(contour)

    coefficient = hullPerimeter/hullArea * radius

    return coefficient > 4.2

def blurAndDisplay(imgGray, cl1):
    imgGrayBlur = cv2.GaussianBlur(imgGray, (7,7), 0)
    imgCl1Blur = cv2.GaussianBlur(cl1, (7,7), 0)

    # Canny Edge Detection
    grayBlurEdges = cv2.Canny(image=imgGrayBlur, threshold1=30, threshold2=200)
    cl1BlurEdges = cv2.Canny(image=imgCl1Blur, threshold1=30, threshold2=200) # Canny Edge Detection

    # Display Canny Edge Detection Image
    return np.concatenate((imgGray, cl1, grayBlurEdges, cl1BlurEdges),axis=1)


if __name__ == '__main__':
    print(len(loopOverImages("./res/cutted_images/unedited/")))
    # imgFiltering("./res/cutted_images/unedited/2019apr04_ecker_sued_10002_16650_bot.png", 
    #              "./res/cutted_images/unedited/2019apr04_ecker_sued_10002_16650_bot_mask.png")