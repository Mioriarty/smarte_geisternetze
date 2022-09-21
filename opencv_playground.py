import cv2
from matplotlib.pyplot import contour
import numpy as np
from PIL import Image
from matplotlib import image

def imgFiltering(url, maskUrl):
    img = cv2.imread(url)
    imgMask = cv2.imread(maskUrl)
    imgMask = cv2.cvtColor(imgMask, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hist = hist=cv2.calcHist(imgGray,[0],None,[256],[0,256])
    clahe = cv2.createCLAHE(clipLimit = 1)
    cl1 = clahe.apply(imgGray)

    imgGray = resize(imgGray)
    imgMask = resize(imgMask)
    cl1 = resize(cl1)

    images = detectEdgesAndDisplay(imgGray, imgMask, cl1)
    display("gray - equalized - edges gray - edges equalized", images)

    # blurredImages = blurAndDisplay(imgGray, cl1)
    # display("blured --- gray - equalized - edges gray - edges equalized", blurredImages)


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

def detectEdgesAndDisplay(imgGray, imgMask, cl1):
    # Canny Edge Detection good values for unedited images th1=75 th2=225
    cl1Edges = cv2.Canny(image=imgGray, threshold1=40, threshold2=50)

    cl1Edges = cv2.bitwise_and(cl1Edges, cl1Edges, mask=imgMask)

    cv2.imshow("contours", np.concatenate((imgGray, cl1Edges),axis=1))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cl1Edges = cv2.morphologyEx(cl1Edges, cv2.MORPH_CLOSE, kernel=np.ones((2,2), np.uint8))
    cl1Edges = cv2.dilate(cl1Edges, kernel=np.ones((3,3), np.uint8), iterations=1)
    contours, hierachy = cv2.findContours(cl1Edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contourImage = np.zeros((cl1Edges.shape[0], cl1Edges.shape[1], 3), dtype=np.uint8)

    for i in range(len(contours)):
        if(isContourLine(contours[i])):
            cv2.drawContours(contourImage, contours, i, (255, 255, 255), 2, cv2.LINE_4, hierachy, 0)


    cv2.imshow("contours", contourImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return np.concatenate((imgGray, cl1, imgMask, cl1Edges),axis=1)

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
    imgFiltering("./res/cutted_images/edited/2019apr04_ecker_sued_10002_5400_bot_blur.png", 
                 "./res/cutted_images/unedited/2019apr04_ecker_sued_10002_5400_bot_mask.png")