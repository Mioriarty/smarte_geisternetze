import cv2
import numpy as np
from PIL import Image
from matplotlib import image

def imgFiltering(url):
    img = cv2.imread(url)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    hist = hist=cv2.calcHist(imgGray,[0],None,[256],[0,256])
    clahe = cv2.createCLAHE(clipLimit = 1)
    cl1 = clahe.apply(imgGray) + 10

    # img_gray = cv2.imread(url, cv2.IMREAD_UNCHANGED)
    # img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)

    # Canny Edge Detection
    grayEdges = cv2.Canny(image=imgGray, threshold1=50, threshold2=600)
    cl1Edges = cv2.Canny(image=cl1, threshold1=60, threshold2=400) # Canny Edge Detection

    # Display Canny Edge Detection Image
    images = np.concatenate((cl1, imgGray, grayEdges, cl1Edges),axis=1)
    cv2.imshow("Images",images)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == '__main__':
    imgFiltering("./res/MARK0000.png")