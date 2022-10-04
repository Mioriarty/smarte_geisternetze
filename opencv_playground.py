import glob
import math
import cv2
import numpy as np
import multiprocessing
from Finding import Finding

# get all image slice and mask paths, run filters and detection on all slices with multiprocessing,
# aggregate findings 
def loopOverImages(dir):
    processes = 8
    sonarTopImgs = glob.glob("{}*top.png".format(dir))
    sonarBotImgs = glob.glob("{}*bot.png".format(dir))

    print("Starting filtering...")
    with multiprocessing.Pool(processes = processes) as pool:
            findingsTop = pool.starmap(imgFiltering, [ (sonarImage, glob.glob("{}_mask.png".format(sonarImage[: - 4]))[0]) for sonarImage in sonarTopImgs ])
            findingsBot = pool.starmap(imgFiltering, [ (sonarImage, glob.glob("{}_mask.png".format(sonarImage[: - 4]))[0]) for sonarImage in sonarBotImgs ])

    findingsTop = sum(findingsTop, [])
    findingsBot = sum(findingsBot, [])
    findings = [ finding for finding in findingsBot + findingsTop if finding != None ]

    return findings

# read image slice and mask, convert them to grayscale, apply histogram equalization, resize the images
# apply non local means denoising
def imgFiltering(url, maskUrl):
    img = cv2.imread(url)
    imgMask = cv2.imread(maskUrl)
    imgMask = cv2.cvtColor(imgMask, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    clahe = cv2.createCLAHE(clipLimit = 1)
    cl1 = clahe.apply(imgGray)

    scaleFactor = 0.4
    imgGray = resize(imgGray, scaleFactor)
    imgMask = resize(imgMask, scaleFactor)
    cl1 = resize(cl1, scaleFactor)

    cl1NlMeanDN = cv2.fastNlMeansDenoising(cl1, dst=True, h=7, searchWindowSize=55)
    contours = detectEdgesAndDisplay(imgMask, cl1NlMeanDN)
    findings = getFinding(contours, url, scaleFactor)

    return findings

# limit contour size and return all contours as findings for one image slice
def getFinding(contours, url, scaleFactor):
    findings = []

    for contour in contours:
        hullArea = cv2.contourArea(cv2.convexHull(contour))

        if hullArea < 200:
            continue

        middle, _ = cv2.minEnclosingCircle(contour)
        xCord = int(middle[0] / scaleFactor)
        yCord = int(middle[1] / scaleFactor)
        
        findings.append(Finding.fromFileName((yCord, xCord), url))

    return findings

# display the image and discard window on key press
def display(windowName, images):
    cv2.imshow(windowName, images)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# resize an image by a scaling factor
def resize(image, scaleFactor):
    width = int(image.shape[1] * scaleFactor)
    height = int(image.shape[0] * scaleFactor)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

# applying bottom detection mask, edge detection and contour filtering
def detectEdgesAndDisplay(imgMask, cl1):

    # Canny Edge Detection good values for unedited images th1=75 th2=225
    cl1Edges = cv2.Canny(image=cl1, threshold1=75, threshold2=225)
    cl1Edges = cv2.bitwise_and(cl1Edges, cl1Edges, mask=imgMask)
    cl1Edges = cv2.morphologyEx(cl1Edges, cv2.MORPH_CLOSE, kernel=np.ones((2,2), np.uint8))
    cl1Edges = cv2.dilate(cl1Edges, kernel=np.ones((3,3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(cl1Edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = [c for c in contours if isContourLine(c)]

    # looping over all contours and only include one contour for all contours in a certain range
    i = 0
    while i < len(contours)-1:
        contours = contours[:i+1] + [ c for c in contours[i+1:] if distance(cv2.minEnclosingCircle(c)[0], cv2.minEnclosingCircle(contours[i])[0]) > 100]
        i+=1

    return contours

# calculating the distance between two points
def distance(mid1, mid2):
    return math.dist(mid2, mid1)

# check if contour satisfies circuference/area * radius condition
def isContourLine(contour):
    hull = cv2.convexHull(contour)
    _, radius = cv2.minEnclosingCircle(contour)

    coefficient = cv2.arcLength(hull, True)/cv2.contourArea(hull) * radius

    return coefficient > 4.2