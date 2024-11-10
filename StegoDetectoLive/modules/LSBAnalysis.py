from PIL import Image
import numpy as np
from scipy.stats import entropy

def get_lsb(image_path):
    img = Image.open(image_path)
    # Convert the image to RGB mode if it's not in that mode.
    img = img.convert("RGB")
    pixels = np.array(img)

    lsb_values = []

    # Extract the LSB from each of the RGB channels of each pixel
    for row in pixels:
        for pixel in row:
            r, g, b = pixel
            lsb_values.append(r & 1)  # LSB of red channel
            lsb_values.append(g & 1)  # LSB of green channel
            lsb_values.append(b & 1)  # LSB of blue channel

    return np.array(lsb_values)

def analyze_lsb(lsb_values):
    # Calculate the entropy of the LSBs
    lsb_entropy = entropy(np.bincount(lsb_values) / len(lsb_values), base=2)

    # Determine if the entropy is low or high
    entropy_label = "Low" if lsb_entropy < 0.9 else "High"

    return lsb_entropy, entropy_label

def analyze_lsb_distribution(lsb_values):
    zero_count = np.sum(lsb_values == 0)
    one_count = np.sum(lsb_values == 1)
    total = len(lsb_values)

    proportion_zero = zero_count / total
    proportion_one = one_count / total

    # Determine if the distribution is even or skewed
    distribution_label = "Even" if abs(proportion_zero - proportion_one) <= 0.1 else "Skewed"

    return proportion_zero, proportion_one, distribution_label

def check_eof_marker(lsb_values):
    eof_marker_1 = [1] * 16 + [0] * 16  # 1111111111111110 (EOF marker)
    eof_marker_2 = [0] * 16 + [0] * 16  # 0000000000000000 (EOF marker)

    # Check if the EOF markers exist in the LSB stream and return the marker
    if any(np.array_equal(lsb_values[i:i + 32], eof_marker_1) for i in range(len(lsb_values) - 31)):
        return True, "1111111111111110"
    elif any(np.array_equal(lsb_values[i:i + 32], eof_marker_2) for i in range(len(lsb_values) - 31)):
        return True, "0000000000000000"
    else:
        return False, None

def lsb_stego_detection(image_path):
    # Extract the LSBs from the image
    lsb_values = get_lsb(image_path)

    # Analyze the LSBs to detect any hidden data
    lsb_entropy, entropy_label = analyze_lsb(lsb_values)
    proportion_zero, proportion_one, distribution_label = analyze_lsb_distribution(lsb_values)
    eof_stego, eof_marker_used = check_eof_marker(lsb_values)

    metadata = {
        "entropy": lsb_entropy,
        "entropy_label": entropy_label,
        "proportion_zero": proportion_zero,
        "proportion_one": proportion_one,
        "distribution_label": distribution_label,
        "eof_marker_detected": eof_stego,
        "eof_marker_used": eof_marker_used
    }

    # Combine all detection results to determine if steganography is present
    is_steganography = entropy_label == "Low" or distribution_label == "Skewed" or eof_stego

    return is_steganography, metadata