import cv2
import numpy as np
import matplotlib
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

img = cv2.imread('MARK0001.png')
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

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

kernel_size = 5
blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

low_threshold = 50
high_threshold = 150
edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
threshold = 15  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 50  # minimum number of pixels making up a line
max_line_gap = 20  # maximum gap in pixels between connectable line segments
line_image = np.copy(img) * 0  # creating a blank to draw lines on

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                        min_line_length, max_line_gap)

for line in lines:
    for x1, y1, x2, y2 in line:
        cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)

cv2.imshow("line_image", line_image)

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
print(i)

cv2.imshow("res", result)
cv2.waitKey(0)
