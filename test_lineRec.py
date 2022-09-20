import cv2
import numpy as np
import matplotlib
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

img = cv2.imread('sDQLM.png')
#converted = convert_hls(img)
image = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
lower = np.uint8([0, 200, 0])
upper = np.uint8([255, 255, 255])
white_mask = cv2.inRange(image, lower, upper)
# yellow color mask
lower = np.uint8([10, 0,   100])
upper = np.uint8([40, 255, 255])
yellow_mask = cv2.inRange(image, lower, upper)
# combine the mask
mask = cv2.bitwise_or(white_mask, yellow_mask)
result = img.copy()
cv2.imshow("mask", mask)

height, width = mask.shape
skel = np.zeros([height, width], dtype=np.uint8)  # [height,width,3]
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
temp_nonzero = np.count_nonzero(mask)
while (np.count_nonzero(mask) != 0):
    eroded = cv2.erode(mask, kernel)
    cv2.imshow("eroded", eroded)
    temp = cv2.dilate(eroded, kernel)
    cv2.imshow("dilate", temp)
    temp = cv2.subtract(mask, temp)
    skel = cv2.bitwise_or(skel, temp)
    mask = eroded.copy()

cv2.imshow("skel", skel)
# cv2.waitKey(0)

edges = cv2.Canny(skel, 50, 150)
cv2.imshow("edges", edges)
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 40,
                        minLineLength=30, maxLineGap=30)
i = 0
for x1, y1, x2, y2 in lines[0]:
    i += 1
    cv2.line(result, (x1, y1), (x2, y2), (255, 0, 0), 1)
print i

cv2.imshow("res", result)
cv2.waitKey(0)
