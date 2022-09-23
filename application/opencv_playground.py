import glob
import cv2
import numpy as np
import multiprocessing
from Finding import Finding

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
    findings = [finding for finding in findingsBot + findingsTop if finding != None ]

    # print(["{} - {}".format(i , finding) for i, finding in enumerate(findings)])

    return findings

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

    # if len(findings) > 0: 
    #     display(str(findings[0].pixelCoord) + url[30:], np.concatenate((imgGray, cl1, image, singlePixel), axis=1))

    return findings

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

def display(windowName, images):
    cv2.imshow(windowName, images)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize(image, scaleFactor):
    width = int(image.shape[1] * scaleFactor)
    height = int(image.shape[0] * scaleFactor)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

def detectEdgesAndDisplay(imgMask, cl1):
    # Canny Edge Detection good values for unedited images th1=75 th2=225
    cl1Edges = cv2.Canny(image=cl1, threshold1=75, threshold2=225)
    cl1Edges = cv2.bitwise_and(cl1Edges, cl1Edges, mask=imgMask)
    cl1Edges = cv2.morphologyEx(cl1Edges, cv2.MORPH_CLOSE, kernel=np.ones((2,2), np.uint8))
    cl1Edges = cv2.dilate(cl1Edges, kernel=np.ones((3,3), np.uint8), iterations=1)
    contours, hierachy = cv2.findContours(cl1Edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # contourImage = np.zeros((cl1.shape[0], cl1.shape[1]), dtype=np.uint8)

    # for i in range(len(contours)):
    #     if(isContourLine(contours[i])):
    #         cv2.drawContours(contourImage, contours, i, (255, 255, 255), 2, cv2.LINE_4, hierachy, 0)

    contours = [c for c in contours if isContourLine(c)]

    i = 0
    while i < len(contours)-1:  
        contours = contours[:i+1] + [ c for c in contours[i+1:] if distance(cv2.minEnclosingCircle(c)[0], cv2.minEnclosingCircle(contours[i])[0]) > 100]
        i+=1


    return contours

def distance(mid1, mid2):
    return int(np.sqrt((mid2[0] - mid1[0])**2 + (mid2[1] - mid1[1])**2))

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