import numpy as np
import cv2
from modules.DatabaseLogic import getSimilarImages

# this function generates a histogram, comparing the pixel values and no. pixels between two images
def histogram(suspect_image: bytes):
    # reads the images, based on the filename
    suspect_image_nparray = np.asarray(bytearray(suspect_image), dtype="uint8")
    img_1 = cv2.imdecode(suspect_image_nparray, cv2.IMREAD_COLOR)

    original_image_path = getSimilarImages(suspect_image_nparray)
    if original_image_path is None:
        return False
    img_2 = cv2.imread(".\\" + original_image_path)

    # initiate the variables
    x1, y1, x2, y2 = [], [], [], []
    calc_dist = []
    dif = 0

    # calculates the histogram to plot, for both images
    histogram_1 = cv2.calcHist([img_1], [0], None, [256], [0, 256])
    histogram_2 = cv2.calcHist([img_2], [0], None, [256], [0, 256])

    # creates a list of the values in the x axis for the histograms
    for n in range(256):
        x1.append(n)
        x2.append(n)

    # adds the pixel values from image 1 to a list
    for xy in histogram_1:
        y1.append(xy[0])

    # adds the pixel values from image 2 to a list
    for xy in histogram_2:
        y2.append(xy[0])

    # changes the type of content in the lists to int
    x1 = [int(i) for i in x1]
    y1 = [int(i) for i in y1]
    x2 = [int(i) for i in x2]
    y2 = [int(i) for i in y2]

    # calculates the difference in the y values, as the x values are a constant 0-256
    for i in range(256):
        dist = y2[i] - y1[i]
        # adds the difference values to a list
        calc_dist.append(dist)
        # calculates the total number of pixels that have been altered
        if calc_dist[i] != 0:
            dif += 1

    # calculates the percentage of pixels that have been altered and rounds the values to 2 decimal places
    percent = (dif / len(calc_dist)) * 100
    r_percent = round(percent, 2)
    print("Total number of changes detected: ", dif, "/", len(calc_dist), " pixels have been altered (", r_percent, "%)")

    if r_percent > 70:
        return True
    else:
        return False