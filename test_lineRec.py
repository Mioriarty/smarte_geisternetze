import cv2
import numpy as np
import matplotlib
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt
import xtf_png

#xtf_png.xtf2png('2019apr04_ecker_sued_10002.xtf', 'formated.png')

img = cv2.imread('MARK0019.png')

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

clahe = cv2.createCLAHE(clipLimit=1)
cl1 = clahe.apply(gray) + 10
clahe_images = np.concatenate((cl1, gray), axis=1)

print(len(cl1))

graycl = cv2.cvtColor(cl1, cv2.COLOR_BGR2GRAY)

kernel_size = 5
blur_gray = cv2.GaussianBlur(graycl, (kernel_size, kernel_size), 0)


low_threshold0 = 0
high_threshold0 = 75
edges0 = cv2.Canny(blur_gray, low_threshold0, high_threshold0)
cv2.imshow("edges0", edges0)


low_threshold1 = 50
high_threshold1 = 150
edges1 = cv2.Canny(blur_gray, low_threshold1, high_threshold1)
cv2.imshow("edges1", edges1)

low_threshold2 = 50
high_threshold2 = 400
edges2 = cv2.Canny(blur_gray, low_threshold2, high_threshold2)
cv2.imshow("edges2", edges2)

cv2.waitKey(0)

"""
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

# Draw the lines on the  image
lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)

cv2.imwrite('detected1.png', lines_edges)
cv2.waitKey(0)
"""
