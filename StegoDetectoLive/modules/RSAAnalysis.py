from PIL import Image
import math
from io import BytesIO

# Function to extract pixel values from an image and organize them into a matrix
def splitpixels(img):
    row_pixels = []
    pixel_matrix = []
    pixel_count = 0

    # Get pixel data from the image
    pixels = img.getdata()

    for pixel in pixels:
        # Append the R, G, B channels as tuples
        row_pixels.append(pixel)

        # Count the number of pixels
        pixel_count += 1

        # If one row is completed, append row_pixels to pixel_matrix
        if pixel_count % img.size[0] == 0:
            pixel_matrix.append(row_pixels)
            row_pixels = []

    print(pixel_count, "pixels")

    return pixel_matrix

# Function to apply a mask to a group of pixels
def groupmask(group_mask, mask):
    # Initialize the new mask variable
    group_mask_new = []

    # Add to the list for the new mask (deep copy for RGB tuples)
    for line in group_mask:
        group_mask_new.append([list(pixel) for pixel in line])

    # Get dimensions of the mask
    totalrow = len(group_mask_new)
    totalcolumn = len(group_mask_new[0])

    # Apply the mask to the group
    for row in range(0, totalrow):
        for column in range(0, totalcolumn):
            for channel in range(3):  # Apply mask to each RGB channel
                if group_mask_new[row][column][channel] % 2 == 0:
                    group_mask_new[row][column][channel] += mask[row][column]
                else:
                    group_mask_new[row][column][channel] -= mask[row][column]

    # Return the calculated mask
    return group_mask_new

# Function to compute the "discrimination function"
def discrimination_function(group):
    # Initialize variables
    amount = 0
    totalrow = len(group)
    totalcolumn = len(group[0])

    # Compute absolute differences across columns (horizontal neighbors)
    for row in range(0, totalrow):
        for column in range(0, totalcolumn - 1):
            for channel in range(3):  # Compute differences for each channel
                amount += abs(group[row][column][channel] - group[row][column + 1][channel])

    # Compute absolute differences across rows (vertical neighbors)
    for column in range(0, totalcolumn):
        for row in range(0, totalrow - 1):
            for channel in range(3):  # Compute differences for each channel
                amount += abs(group[row][column][channel] - group[row + 1][column][channel])

    return amount

def breakimage(imagearray, maskk, position):
    brokeimage = []

    # Initialize the new image subset with the same structure as the mask
    for line in maskk:
        brokeimage.append([[0] * 3 for _ in line])  # Initialize with dummy RGB values

    # Extract pixel values corresponding to the mask from the image
    for temprow in range(len(maskk)):
        for tempcol in range(len(maskk[0])):
            pixel = imagearray[temprow + position[0]][tempcol + position[1]]
            # Ensure consistency between grayscale and RGB formats
            if isinstance(pixel, int):  # Grayscale pixel
                brokeimage[temprow][tempcol] = [pixel, pixel, pixel]  # Duplicate grayscale value to RGB
            else:  # RGB pixel
                brokeimage[temprow][tempcol] = list(pixel)

    return brokeimage

def analyseLSBs(imageBox, mask, neg_mask):
    # Initialize counters for different types of pixel groups
    reg_pos_2 = 0  # Count of regular groups for the positive mask
    sing_pos_2 = 0  # Count of singular groups for the positive mask
    reg_flip_pos_2 = 0  # Count of regular groups for the flipped positive mask
    sing_flip_pos_2 = 0  # Count of singular groups for the flipped positive mask
    neg_reg_pos_2 = 0  # Count of regular groups for the negative mask
    neg_sing_pos_2 = 0  # Count of singular groups for the negative mask
    neg_reg_flip_pos_2 = 0  # Count of regular groups for the flipped negative mask
    neg_sing_flip_pos_2 = 0  # Count of singular groups for the flipped negative mask

    # Get dimensions of the image
    imageRow = len(imageBox)
    imageCol = len(imageBox[0])

    # Get dimensions of the mask
    maskRow = len(mask)
    maskCol = len(mask[0])

    num = float((imageRow - imageRow % maskRow) / maskRow * (imageCol - imageCol % maskCol) / maskCol)

    numCount = 0

    for row in range(0, imageRow):
        for column in range(0, imageCol):
            if (row + 1) % maskRow == 0 and (column + 1) % maskCol == 0:
                # This is the start of the group
                pos = [row - maskRow + 1, column - maskCol + 1]

                # Increment the number of groups
                numCount += 1

                # Extract the mask group
                breakimagebox = breakimage(imageBox, mask, pos)

                flip_box = []
                # Copy breakimagebox into flip_box
                for line in breakimagebox:
                    flip_box.append([list(pixel) for pixel in line])

                # Flip pixel values in the group using F1 operation
                for fliprow in range(0, len(breakimagebox)):
                    for flipcolumn in range(0, len(breakimagebox[0])):
                        for channel in range(3):  # Flip each channel
                            if breakimagebox[fliprow][flipcolumn][channel] % 2 == 0:
                                flip_box[fliprow][flipcolumn][channel] += 1
                            else:
                                flip_box[fliprow][flipcolumn][channel] -= 1

                # Apply the discrimination function
                discr_breakimagebox = discrimination_function(breakimagebox)
                discr_mask_breakimagebox = discrimination_function(groupmask(breakimagebox, mask))
                discr_neg_mask_breakimagebox = discrimination_function(groupmask(breakimagebox, neg_mask))
                discr_flip_box = discrimination_function(flip_box)
                discr_mask_flip_box = discrimination_function(groupmask(flip_box, mask))
                discr_neg_mask_flip_box = discrimination_function(groupmask(flip_box, neg_mask))

                # Classify groups based on discrimination values
                if discr_breakimagebox > discr_mask_breakimagebox:
                    sing_pos_2 += 1
                elif discr_breakimagebox < discr_mask_breakimagebox:
                    reg_pos_2 += 1

                if discr_breakimagebox > discr_neg_mask_breakimagebox:
                    neg_sing_pos_2 += 1
                elif discr_breakimagebox < discr_neg_mask_breakimagebox:
                    neg_reg_pos_2 += 1

                if discr_flip_box > discr_mask_flip_box:
                    sing_flip_pos_2 += 1
                elif discr_flip_box < discr_mask_flip_box:
                    reg_flip_pos_2 += 1

                if discr_flip_box < discr_neg_mask_flip_box:
                    neg_reg_flip_pos_2 += 1
                elif discr_flip_box > discr_neg_mask_flip_box:
                    neg_sing_flip_pos_2 += 1

    if num == 0:
        return 0

    # Solve the quadratic equation to estimate the message length
    d0 = float(reg_pos_2 - sing_pos_2) / num
    dn0 = float(neg_reg_pos_2 - neg_sing_pos_2) / num
    d1 = float(reg_flip_pos_2 - sing_flip_pos_2) / num
    dn1 = float(neg_reg_flip_pos_2 - neg_sing_flip_pos_2) / num

    a = 2 * (d1 + d0)
    b = (dn0 - dn1 - d1 - 3 * d0)
    c = (d0 - dn0)

    if b * b < 4 * a * c or a == 0:
        message_length = 0
    else:
        quadratic_solution1 = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
        quadratic_solution2 = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
        if abs(quadratic_solution1) < abs(quadratic_solution2):
            quadratic_solution = quadratic_solution1
        else:
            quadratic_solution = quadratic_solution2

        message_length = abs(quadratic_solution / (quadratic_solution - 0.50))

    return message_length

def image_analyser(img: bytes, masks):
    image_filename = Image.open(BytesIO(img)).convert("RGB")

    width, height = image_filename.size

    # Select the appropriate mask based on the image dimensions
    if width < 128 or height < 128:
        chosen_mask = masks[0]  # Use m0 for images smaller than 128x128
    elif width < 512 or height < 512:
        chosen_mask = masks[1]  # Use m1 for images smaller than 512x512
    else:
        chosen_mask = masks[2]  # Use m2 for images 512x512 or larger

    # Print debug information
    print(f"Image dimensions: {width}x{height}")
    print(f"Chosen mask size: {len(chosen_mask)}x{len(chosen_mask[0])}")

    # Generate the negative mask
    neg_mask = []
    for l in chosen_mask:
        neg_mask.append(list(l))

    for r in range(len(neg_mask)):
        for c in range(len(neg_mask[0])):
            if neg_mask[r][c] == 1:
                neg_mask[r][c] = -1
            elif neg_mask[r][c] == -1:
                neg_mask[r][c] = 1

    pix = splitpixels(image_filename)

    print("")
    print("Analysing LSBs")

    gpercent = analyseLSBs(pix, chosen_mask, neg_mask)
    metadata = {
        "width": width,
        "height": height,
        "total_pixels": width * height,
        "mask_size": (len(chosen_mask), len(chosen_mask[0])),
        "gpercent": gpercent,
    }
    print("")
    if gpercent == 0:
        print("Unable to calculate the percent of the pixels")
        encodedpercent = "?"
        return encodedpercent,False,metadata
    else:
        encodedpercent = gpercent
        print("")
        totalpercent = (encodedpercent * 100)
        print("Total Percent of pixels likely to contain embedded data: {:.3f}%".format(totalpercent))
        totalpix = width * height
        data = (encodedpercent * totalpix)
        print("Approximately {:.3f} bits of data".format(data))
        print("Encoded Percent: {:.3f}".format(encodedpercent))

        if encodedpercent < 0.07:
            return False,metadata
        else:
            return True,metadata




# Masks
# masks = [
#     [[0, 1], [1, 0]],  # m0
#     [[0, 1, 1, 0]],  # m1
#     [[0, 0, 0], [0, 1, 0], [0, 0, 0]]  # m2
# ]
#
#
#
# #Testing
# #print("TEST")
# with open("../Stego Images/testing.png", "rb") as f:
#     image_bytes = f.read()
#
#
# # Analyze the image using bytes
# result = image_analyser(image_bytes, masks)
# print("Result:", result)
