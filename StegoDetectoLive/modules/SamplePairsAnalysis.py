import numpy as np
from PIL import Image
from io import BytesIO
import math


def analysis(image_bytes: bytes, colour: int):
    # Load image from bytes and greyscale it
    img = Image.open(BytesIO(image_bytes))
    img_array = np.array(img)
    height = img.height
    width = img.width

    P = X = Y = Z = W = 0

    for row in range(height):
        for col in range(0, width - 1, 2):
            # Get rgb values of pixel pair
            pixel1 = img_array[row, col]
            pixel2 = img_array[row, col + 1]

            colour_pixel1 = pixel1[colour]
            colour_pixel2 = pixel2[colour]

            msb_mask = 0b11111110
            if (colour_pixel1 & msb_mask) == (colour_pixel2 & msb_mask) and (colour_pixel1 & 1) != (colour_pixel2 & 1):
                W += 1
            if colour_pixel1 == colour_pixel2:
                Z += 1
            if (colour_pixel2 & 1 == 0 and colour_pixel1 < colour_pixel2) or (
                    colour_pixel2 & 1 != 0 and colour_pixel1 > colour_pixel2):
                X += 1
            if (colour_pixel2 & 1 == 0 and colour_pixel1 > colour_pixel2) or (
                    colour_pixel2 & 1 != 0 and colour_pixel1 < colour_pixel2):
                Y += 1
            P += 1

    for row in range(0, height - 1, 2):
        for col in range(width):
            # Get rgb values of pixel pair
            pixel1 = img_array[row, col]
            pixel2 = img_array[row + 1, col]

            colour_pixel1 = pixel1[colour]
            colour_pixel2 = pixel2[colour]

            msb_mask = 0b11111110
            if (colour_pixel1 & msb_mask) == (colour_pixel2 & msb_mask) and (colour_pixel1 & 1) != (colour_pixel2 & 1):
                W += 1
            if colour_pixel1 == colour_pixel2:
                Z += 1
            if (colour_pixel2 & 1 == 0 and colour_pixel1 < colour_pixel2) or (
                    colour_pixel2 & 1 != 0 and colour_pixel1 > colour_pixel2):
                X += 1
            if (colour_pixel2 & 1 == 0 and colour_pixel1 > colour_pixel2) or (
                    colour_pixel2 & 1 != 0 and colour_pixel1 < colour_pixel2):
                Y += 1
            P += 1

    a = 0.5 * (W + Z)
    b = 2 * X - P
    c = Y - X
    if a == 0:
        x = c / b
    discriminant = pow(b, 2) - (4 * a * c)
    if discriminant >= 0:
        rootpos = ((-1 * b) + math.sqrt(discriminant)) / (2 * a)
        rootneg = ((-1 * b) - math.sqrt(discriminant)) / (2 * a)
        if abs(rootpos) <= abs(rootneg):
            x = rootpos
        else:
            x = rootneg
    else:
        x = c / b

    if x == 0:
        x = c / b
    return x


def detect_stego(image_bytes: bytes):
    red_results = analysis(image_bytes, 0)
    green_results = analysis(image_bytes, 1)
    blue_results = analysis(image_bytes, 2)
    average = (red_results + green_results + blue_results) / 3

    metadata = {
        "Red": red_results,
        "Green": green_results,
        "Blue": blue_results,
        "Average": average
    }

    if average > 0.1:
        return True, metadata
    return False, metadata
