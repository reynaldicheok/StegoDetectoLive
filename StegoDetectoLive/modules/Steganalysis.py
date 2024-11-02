
from PIL import Image
import math
import sys
from matplotlib import pyplot as plt
import cv2
import scipy.stats


# this function displays the main menu that the user uses to choose which test to run
def mainmenu():
    print("**********MAIN MENU**********")
    print("Please select an option.")
    print()
    print("1 : Histogram Analysis")
    print("2 : Chi-Square Test")
    print("3 : RS Steganalysis")
    print("4 : Exit")


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

import sys
import math
import numpy as np
from PIL import Image

# Calculates a 'discrimination' value for a group of pixels by comparing adjacent values
def discrimination_function(group):
    # Initialize the total discrimination amount
    amount = 0
    total_rows = len(group)
    total_columns = len(group[0])

    # Calculate discrimination for each pair of adjacent columns
    for row in range(total_rows):
        for column in range(total_columns - 1):  # Avoid index out-of-range error
            amount += abs(group[row][column] - group[row][column + 1])

    # Calculate discrimination for each pair of adjacent rows
    for column in range(total_columns):
        for row in range(total_rows - 1):
            amount += abs(group[row][column] - group[row + 1][column])

    return amount

# Applies a mask to a group of pixels to generate a new group mask
def groupmask(group, mask):
    # Copy the original group structure
    new_mask = [list(row) for row in group]

    # Apply the mask by adjusting even and odd values accordingly
    for row in range(len(new_mask)):
        for col in range(len(new_mask[0])):
            if new_mask[row][col] % 2 == 0:  # If value is even
                new_mask[row][col] += mask[row][col]
            else:  # If value is odd
                new_mask[row][col] -= mask[row][col]

    return new_mask

# Extracts a section of the image based on a position and mask size
def breakimage(image_array, mask, position):
    # Initialize the section of the image to return
    image_section = [list(row) for row in mask]

    # Fill in values from the image at the specified position
    for row in range(len(mask)):
        for col in range(len(mask[0])):
            image_section[row][col] = image_array[row + position[0]][col + position[1]]

    return image_section

# Splits an image into separate arrays for red, green, and blue channels
def splitpixels(img):
    # Retrieve the RGB data for each pixel in the image
    rgb_data = img.getdata()
    width, height = img.size
    print(f"Size: {width} x {height} (Total Pixels: {width * height})")

    # Initialize lists for each color channel
    red_channel, green_channel, blue_channel = [], [], []

    for pixel in rgb_data:
        # Split the RGB values and add to corresponding color lists
        red_channel.append(pixel[0])
        green_channel.append(pixel[1] if len(pixel) > 1 else 0)  # Check if grayscale
        blue_channel.append(pixel[2] if len(pixel) > 2 else 0)   # Check if grayscale

    return red_channel, green_channel, blue_channel

# Analyzes the image for the presence of embedded information
def analyseimage(img_path, mask, discriminator_overlap):
    img =Image.open(img_path)
    # Generate a negative version of the mask
    negative_mask = [[-value if value else value for value in row] for row in mask]

    # Split image into red, green, blue channels
    red, green, blue = splitpixels(img)

    # Analyze each color channel individually
    red_percent = analyseLSBs(red, mask, negative_mask, discriminator_overlap)
    green_percent = analyseLSBs(green, mask, negative_mask, discriminator_overlap)
    blue_percent = analyseLSBs(blue, mask, negative_mask, discriminator_overlap)

    # Calculate the average likelihood of embedded information across channels
    if red_percent and green_percent and blue_percent:
        encoded_percent = (red_percent + green_percent + blue_percent) / 3
        print(f"Estimated pixels with embedded data: {encoded_percent * 100:.2f}%")
    else:
        print("Unable to calculate embedded data likelihood for all channels.")
        encoded_percent = 0

    return encoded_percent

# Analyzes pixel groups for potential embedded information using LSB flipping
def analyseLSBs(imagebox, mask, neg_mask, discriminator_overlap):
    r_p2 = s_p2 = r_1p2 = s_1p2 = neg_r_p2 = neg_s_p2 = neg_r_1p2 = neg_s_1p2 = 0
    im_rows, im_cols = len(imagebox), len(imagebox[0])
    mask_rows, mask_cols = len(mask), len(mask[0])

    if discriminator_overlap:
        num_groups = (im_rows - mask_rows + 1) * (im_cols - mask_cols + 1)
    else:
        num_groups = (im_rows // mask_rows) * (im_cols // mask_cols)

    print(f"Number of groups to check = {num_groups}")

    for row in range(im_rows - (mask_rows if discriminator_overlap else 0)):
        for col in range(im_cols - (mask_cols if discriminator_overlap else 0)):
            if discriminator_overlap or ((row + 1) % mask_rows == 0 and (col + 1) % mask_cols == 0):
                pos = [row, col] if discriminator_overlap else [row - mask_rows + 1, col - mask_cols + 1]
                group = breakimage(imagebox, mask, pos)

                # Flip the least significant bit (LSB) in each pixel
                flipped_group = [[value ^ 1 for value in row] for row in group]

                # Calculate discrimination values
                discr_group = discrimination_function(group)
                discr_mask_group = discrimination_function(groupmask(group, mask))
                discr_neg_mask_group = discrimination_function(groupmask(group, neg_mask))
                discr_flipped_group = discrimination_function(flipped_group)
                discr_mask_flipped_group = discrimination_function(groupmask(flipped_group, mask))
                discr_neg_mask_flipped_group = discrimination_function(groupmask(flipped_group, neg_mask))

                # Classify groups based on calculated discrimination values
                s_p2 += discr_group > discr_mask_group
                r_p2 += discr_group < discr_mask_group
                neg_s_p2 += discr_group > discr_neg_mask_group
                neg_r_p2 += discr_group < discr_neg_mask_group
                s_1p2 += discr_flipped_group > discr_mask_flipped_group
                r_1p2 += discr_flipped_group < discr_mask_flipped_group
                neg_s_1p2 += discr_flipped_group > discr_neg_mask_flipped_group
                neg_r_1p2 += discr_flipped_group < discr_neg_mask_flipped_group

                # Output progress for every 1000 groups processed
                if (row * im_cols + col + 1) % 1000 == 0:
                    sys.stdout.write(f'\rGroups checked so far = {row * im_cols + col + 1}')

    # Using a quadratic equation, estimate the presence of embedded data
    d0 = (r_p2 - s_p2) / num_groups
    dn0 = (neg_r_p2 - neg_s_p2) / num_groups
    d1 = (r_1p2 - s_1p2) / num_groups
    dn1 = (neg_r_1p2 - neg_s_1p2) / num_groups

    a, b, c = 2 * (d1 + d0), (dn0 - dn1 - d1 - 3 * d0), (d0 - dn0)

    if b * b < 4 * a * c or a == 0:
        message_length = 0  # Avoid negative root or division by zero
    else:
        solution = max((-b + math.sqrt(b * b - 4 * a * c)) / (2 * a), (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a))
        message_length = abs(solution / (solution - 0.5)) if solution != 0.5 else 0

    return message_length
# return the value of each pixel in the image
def splitpixels(img):
    pixRow = []
    pix = []
    pixNum = 0

    # getting the pixels from the image
    pixels = img.getdata()

    for pixel in pixels:
        # png
        if isinstance(pixel, int):
            # appending the value of each pixel in pixRow
            pixRow.append(pixel)

        # jpg
        else:
            pixRow.append(pixel[0])

        # counting the no.of pixels
        pixNum += 1

        # If one rows is completed, then we append pixRow to pix and
        # clear pixRow for next row of pixels
        if pixNum % img.size[0] == 0:
            pix.append(pixRow)
            pixRow = []

    print(pixNum, "pixels")

    return pix


def groupmask(gmask, mask):
    # gmask-->group
    # initialise the new mask variable
    newgroupmask = []

    # adds to the list for the new mask
    # copied group to newgroupmask
    for line in gmask:
        newgroupmask.append(list(line))

    # sets the row and column values
    totalrow = len(newgroupmask)
    totalcolumn = len(newgroupmask[0])

    # applying the mask on the group
    for row in range(0, totalrow):
        for column in range(0, totalcolumn):
            if newgroupmask[row][column] % 2 == 0:
                newgroupmask[row][column] += mask[row][column]
            else:
                newgroupmask[row][column] -= mask[row][column]

    # returns the calculated mask
    return newgroupmask


# finding the difference between the pixel values in the group-->sum(abs(x(i+1)-x(i-1)))
def discrimination_function(group):
    # initialise variables
    amount = 0
    totalrow = len(group)
    totalcolumn = len(group[0])

    # cycles through the columns using the discrimination function
    for row in range(0, totalrow):
        for column in range(0, totalcolumn):
            if column < (totalcolumn - 1):
                amount += abs(group[row][column] - group[row][column + 1])
    # cycles through the rows using the discrimination function
    for column in range(0, totalcolumn):
        for row in range(0, totalrow):
            if row < (totalrow - 1):
                amount += abs(group[row][column] - group[row + 1][column])
    return amount


def breakimage(imagearray, maskk, position):
    # position is the start of the group
    # initiate a new list
    brokeimage = []

    # copy mask rows into brokeimage
    # brokeimage = [[0, 1, 0]]
    for line in maskk:
        brokeimage.append(list(line))

    # cycles through the image with the chosen mask to break the image
    for temprow in range(0, len(maskk)):
        for tempcol in range(0, len(maskk[0])):
            brokeimage[temprow][tempcol] = imagearray[temprow + position[0]][tempcol + position[1]]

    return brokeimage


def analyseLSBs(imageBox, mask, neg_mask):
    # r(p/2), s(p/2), r(1-p/2), s(1-p/2) and their negations
    r_p2 = 0
    s_p2 = 0
    r_1p2 = 0
    s_1p2 = 0
    neg_r_p2 = 0
    neg_s_p2 = 0
    neg_r_1p2 = 0
    neg_s_1p2 = 0

    # getting the dimesions of the image
    imageRow = len(imageBox)
    # 0th element is a list so it tells us the no.of columns
    imageCol = len(imageBox[0])

    # getting the dimensions of the mask
    maskRow = len(mask)
    maskCol = len(mask[0])

    num = float((imageRow - imageRow % maskRow) / maskRow * (imageCol - imageCol % maskCol) / maskCol)

    # 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1
    # 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1
    # 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1
    # 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1 2 3 4 1

    numCount = 0

    for row in range(0, imageRow):
        for column in range(0, imageCol):

            if (row + 1) % maskRow == 0:
                if (column + 1) % maskCol == 0:
                    # this is the start of the group
                    pos = [row - maskRow + 1, column - maskCol + 1]

                    # number of groups
                    numCount += 1

                    # taking the mask group
                    breakimagebox = breakimage(imageBox, mask, pos)

                    flip_box = []
                    # copying the breakimagebox in flip_box
                    for line in breakimagebox:
                        flip_box.append(list(line))

                    # flipping the values of the pixels in the group using F1 operation(0<->1,2<->3 ,..., 254<->255)
                    for fliprow in range(0, len(breakimagebox)):
                        for flipcolumn in range(0, len(breakimagebox[0])):
                            if breakimagebox[fliprow][flipcolumn] % 2 == 0:
                                flip_box[fliprow][flipcolumn] += 1
                            elif breakimagebox[fliprow][flipcolumn] % 2 == 1:
                                flip_box[fliprow][flipcolumn] += -1

                    # The below code is used to find the no of singular groups and regular groups when there is 50% and 100% embedding(code 214-262)
                    # f(G)
                    # applying the discrimination function on the group
                    discr_breakimagebox = discrimination_function(breakimagebox)

                    # f(G_m)
                    # applied the mask on the group and then applied the discrimination function
                    discr_mask_breakimagebox = discrimination_function(groupmask(breakimagebox, mask))

                    # f(G_(-m))
                    # applying negative mask on the group and applying the discrimination function
                    discr_neg_mask_breakimagebox = discrimination_function(groupmask(breakimagebox, neg_mask))

                    # f(F(G))
                    # applying the discrimination function on the flipped group
                    discr_flip_box = discrimination_function(flip_box)

                    # f(F(G)_m)
                    # applying the mask on the flipped pixel group and then applying the discrimination function
                    discr_mask_flip_box = discrimination_function(groupmask(flip_box, mask))

                    # f(F(G)_(-m))
                    # applying the negative mask on the flipped group and then applying the discrimination function
                    discr_neg_mask_flip_box = discrimination_function(groupmask(flip_box, neg_mask))

                    # normal image
                    # f(G) > f(G_m)  -> singular group
                    if discr_breakimagebox > discr_mask_breakimagebox:
                        s_p2 += 1
                    # f(G_m) > f(G) -> regular group
                    elif discr_breakimagebox < discr_mask_breakimagebox:
                        r_p2 += 1

                    # f(G) > f(G_(-m)) -> negative singular group
                    if discr_breakimagebox > discr_neg_mask_breakimagebox:
                        neg_s_p2 += 1
                    # f(G_(-m)) > f(G) -> negative regular group
                    elif discr_breakimagebox < discr_neg_mask_breakimagebox:
                        neg_r_p2 += 1

                    # flipped image with mask m
                    # image group F1 operation followed by mask and discrimination
                    # f(F(G)) > f(F(G)_(m))
                    if discr_flip_box > discr_mask_flip_box:
                        s_1p2 += 1
                    elif discr_flip_box < discr_mask_flip_box:
                        r_1p2 += 1

                    # flipped image with mask -m
                    if discr_flip_box < discr_neg_mask_flip_box:
                        neg_r_1p2 += 1
                    elif discr_flip_box > discr_neg_mask_flip_box:
                        neg_s_1p2 += 1

    if num == 0:
        return 0

    # finding the message length by solving the quadratic
    d0 = float(r_p2 - s_p2) / num
    dn0 = float(neg_r_p2 - neg_s_p2) / num
    d1 = float(r_1p2 - s_1p2) / num
    dn1 = float(neg_r_1p2 - neg_s_1p2) / num

    a = 2 * (d1 + d0)
    b = (dn0 - dn1 - d1 - 3 * d0)
    c = (d0 - dn0)

    if b * b < 4 * a * c:
        # avoid negative root
        message_length = 0
    elif a == 0:
        # avoid deviding by zero
        message_length = 0
    else:
        # x = (-b+- sqrt(b^2-4ac))/2a, quadratic
        quadratic_solution1 = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
        quadratic_solution2 = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
        if abs(quadratic_solution1) < abs(quadratic_solution2):
            quadratic_solution = quadratic_solution1
        else:
            quadratic_solution = quadratic_solution2
        # p = x/(x−1/2), where p is message length
        message_length = abs(quadratic_solution / (quadratic_solution - 0.50))

    return message_length


def image_analyser(img, chosen_mask):
    # chosen_mask = [[0, 1, 0]]
    neg_mask = []

    # neg_mask = [[0, 1, 0]]
    for l in chosen_mask:
        neg_mask.append(list(l))

    # neg_mask = [[0, -1, 0]]
    for r in range(len(neg_mask)):
        for c in range(len(neg_mask[0])):
            if neg_mask[r][c] == 1:
                neg_mask[r][c] = -1
            elif neg_mask[r][c] == -1:
                neg_mask[r][c] = 1

    pix = splitpixels(img)

    # displays the size of the chosen mask
    print("")
    print("Mask size = ", len(chosen_mask[0]), "x", len(chosen_mask))

    # analyses the pixels to determine what percent of them may contain embedded content
    print("")
    print("Analysing LSBs")
    gpercent = analyseLSBs(pix, chosen_mask, neg_mask)

    # controls any errors within the calculations
    print("")
    # if message length is 0
    if gpercent == 0:
        print("Unable to calculate the percent of the pixels")

        print("")
        encodedpercent = "?"
    else:
        # calculates and displays the total percentage of pixels that are likely to be encoded
        encodedpercent = gpercent
        print("")
        totalpercent = (encodedpercent * 100)
        print("Total Percent of pixels likely to contain embedded data: ", round(totalpercent, 2), "%")
        width, height = img.size
        totalpix = int(width) * int(height)
        # the size of the file is calculated by multiplying the percent of encoded pixels by the total number of pixels

        data = ((encodedpercent * totalpix))
        print("Approximately ", round(data, 2), " bits of data")

    return encodedpercent


def quadratic_solution(a, b, c):
    d = (b**2) - (4 * a * c)
    sol1 = ((-b - cmath.sqrt(d)) / (2*a))
    sol2 = ((-b + cmath.sqrt(d)) / (2*a))

    return sol2.real, sol1.real

img_r = ocv.imread("./steganography_image.png", ocv.IMREAD_GRAYSCALE)
threshold = 0

dimensions = img_r.shape
img_height = dimensions[0]
img_width = dimensions[1]

P = []

for i in range(0, img_height):
    for j in range(0, img_width-1):
        c1 = img_r[i, j]
        c2 = img_r[i, j + 1]
        P.append((c1, c2))

x = y = kp = 0

for k in range(0, (img_height * (img_width-1))):
    (r, s) = P[k]
    if(((s % 2 == 0) and (r < s)) or ((s % 2 != 0) and (r > s))):
        x += 1
    elif(((s % 2 == 0) and (r > s)) or ((s % 2 != 0) and (r < s))):
        y += 1
    elif((s // 2) == (r // 2)):
        kp += 1

if kp == 0:
    print("SPA Failed because k = 0")

a = 2 * kp
b = 2 * (2 * x - img_height*(img_width-1))
c = y - x

betaP, betaM = quadratic_solution(a, b, c)
beta = min(betaP, betaM)
print("Change Rate of Stego Image: " + str(beta))
# opened the image file
image_filename = Image.open("./steganography_image.png")

# mask defined
m2 = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]

image_analyser(image_filename, m2)
histogram("./steganography_image.png","Monalisa.png")
