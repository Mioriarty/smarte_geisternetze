import cv2
from PIL import Image
from matplotlib import image

def imgFiltering(url):
    img = cv2.imread(url)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img_gray = cv2.imread(url, cv2.IMREAD_UNCHANGED)
    # img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)

    # Canny Edge Detection
    edges = cv2.Canny(image=img_gray, threshold1=50, threshold2=500) # Canny Edge Detection

    # Display Canny Edge Detection Image
    cv2.imshow('Canny Edge Detection', edges)
    cv2.waitKey(0)

    cv2.destroyAllWindows()



if __name__ == '__main__':
    imgFiltering("./res/MARK0000.png")