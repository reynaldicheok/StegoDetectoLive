from matplotlib import pyplot as plt
import cv2
from PIL import Image
# this function generates a histogram, comparing the pixel values and no. pixels between two images
def histogram(suspect_image, original_image):
    # reads the images, based on the filename
    img_1 = cv2.imread(suspect_image)
    img_2 = cv2.imread(original_image)

    # initiate the variables
    x1, y1, x2, y2 = [], [], [], []
    calc_dist = []
    dif = 0

    # calculates the histogram to plot, for both images
    histogram_1 = cv2.calcHist([img_1], [0], None, [256], [0, 256])
    histogram_2 = cv2.calcHist([img_2], [0], None, [256], [0, 256])

    # plots the histogram and adds the labels for both lines
    plt.plot(histogram_1, label="Suspicious Image")
    plt.plot(histogram_2, label="Original Image")
    plt.xlabel("Pixel Value")
    plt.ylabel("No. Pixels")
    plt.legend(loc='upper left')

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

    # displays the histogram of image 1 and 2
    plt.show()

    # plots, labels and displays the difference values
    plt.plot(x1, calc_dist, label="Difference")
    plt.xlabel("Pixel Value")
    plt.ylabel("Difference")
    plt.show()

histogram("./steganography_image.png","Monalisa.png")