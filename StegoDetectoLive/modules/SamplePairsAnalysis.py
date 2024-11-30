import numpy as np
from PIL import Image
from io import BytesIO
import math


def analysis(image_bytes: bytes, colour: int):
    # Load image from bytes and greyscale it
    img = Image.open(BytesIO(image_bytes))
    img_array = np.array(img)
    image_height = img.height
    image_width = img.width

    total_pairs = group_x = group_y = group_z = group_w = 0

    for row in range(image_height):
        for col in range(0, image_width - 1, 2):
            # Get rgb values of pixel pair
            pixel1 = img_array[row, col]
            pixel2 = img_array[row, col + 1]

            channel_pixel1 = pixel1[colour]
            channel_pixel2 = pixel2[colour]

            msb_mask = 0b11111110
            if (channel_pixel1 & msb_mask) == (channel_pixel2 & msb_mask) and (channel_pixel1 & 1) != (channel_pixel2 & 1):
                group_w += 1
            if channel_pixel1 == channel_pixel2:
                group_z += 1
            if (channel_pixel2 & 1 == 0 and channel_pixel1 < channel_pixel2) or (
                    channel_pixel2 & 1 != 0 and channel_pixel1 > channel_pixel2):
                group_x += 1
            if (channel_pixel2 & 1 == 0 and channel_pixel1 > channel_pixel2) or (
                    channel_pixel2 & 1 != 0 and channel_pixel1 < channel_pixel2):
                group_y += 1
            total_pairs += 1

    for row in range(0, image_height - 1, 2):
        for col in range(image_width):
            # Get rgb values of pixel pair
            pixel1 = img_array[row, col]
            pixel2 = img_array[row + 1, col]

            channel_pixel1 = pixel1[colour]
            channel_pixel2 = pixel2[colour]

            msb_mask = 0b11111110
            if (channel_pixel1 & msb_mask) == (channel_pixel2 & msb_mask) and (channel_pixel1 & 1) != (channel_pixel2 & 1):
                group_w += 1
            if channel_pixel1 == channel_pixel2:
                group_z += 1
            if (channel_pixel2 & 1 == 0 and channel_pixel1 < channel_pixel2) or (
                    channel_pixel2 & 1 != 0 and channel_pixel1 > channel_pixel2):
                group_x += 1
            if (channel_pixel2 & 1 == 0 and channel_pixel1 > channel_pixel2) or (
                    channel_pixel2 & 1 != 0 and channel_pixel1 < channel_pixel2):
                group_y += 1
            total_pairs += 1

    a = 0.5 * (group_w + group_z)
    b = 2 * group_x - total_pairs
    c = group_y - group_x
    if a == 0:
        solution_x = c / b
    discriminant = pow(b, 2) - (4 * a * c)
    if discriminant >= 0:
        root_positive = ((-1 * b) + math.sqrt(discriminant)) / (2 * a)
        root_negative = ((-1 * b) - math.sqrt(discriminant)) / (2 * a)
        if abs(root_positive) <= abs(root_negative):
            solution_x = root_positive
        else:
            solution_x = root_negative
    else:
        solution_x = c / b

    if solution_x == 0:
        solution_x = c / b
    return solution_x


def detect_stego(image_bytes: bytes):
    red_results = analysis(image_bytes, 0)
    green_results = analysis(image_bytes, 1)
    blue_results = analysis(image_bytes, 2)
    average_result = (red_results + green_results + blue_results) / 3

    metadata = {
        "Red": red_results,
        "Green": green_results,
        "Blue": blue_results,
        "Average": average_result
    }

    if average_result > 0.1:
        return True, metadata
    return False, metadata
