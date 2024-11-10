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

    print(f"LSB Entropy: {lsb_entropy}")

    # If the entropy is low (indicating less randomness), it could be a sign of hidden data.
    if lsb_entropy < 0.9:
        return "Potential steganography detected: Low entropy (less randomness)."
    else:
        return "No steganography detected: High entropy (random)."

def analyze_lsb_distribution(lsb_values):
    zero_count = np.sum(lsb_values == 0)
    one_count = np.sum(lsb_values == 1)
    total = len(lsb_values)

    proportion_zero = zero_count / total
    proportion_one = one_count / total

    print(f"Proportion of 0s: {proportion_zero:.4f}, Proportion of 1s: {proportion_one:.4f}")

    # If one value is overwhelmingly more frequent than the other, it might indicate hidden data.
    if abs(proportion_zero - proportion_one) > 0.1:
        return "Potential steganography detected: Skewed distribution of LSBs."
    else:
        return "No steganography detected: Even distribution of LSBs."

def check_eof_marker(lsb_values):
    eof_marker_1 = [1] * 16 + [0] * 16  # 1111111111111110 (EOF marker)
    eof_marker_2 = [0] * 16 + [0] * 16  # 0000000000000000 (EOF marker)

    # Check if the EOF markers exist in the LSB stream
    if any(np.array_equal(lsb_values[i:i + 32], eof_marker_1) for i in range(len(lsb_values) - 31)):
        return "Potential steganography detected: EOF marker (1111111111111110) found."
    elif any(np.array_equal(lsb_values[i:i + 32], eof_marker_2) for i in range(len(lsb_values) - 31)):
        return "Potential steganography detected: EOF marker (0000000000000000) found."
    else:
        return "No EOF marker detected: No obvious end of message."

def lsb_stego_detection(image_path):
    # Extract the LSBs from the image
    lsb_values = get_lsb(image_path)

    # Analyze the LSBs to detect any hidden data
    entropy_result = analyze_lsb(lsb_values)
    distribution_result = analyze_lsb_distribution(lsb_values)
    eof_result = check_eof_marker(lsb_values)

    # Combine results for a more comprehensive detection
    if "Potential steganography" in entropy_result or "Potential steganography" in distribution_result or "Potential steganography" in eof_result:
        return f"Potential steganography detected!\n{entropy_result}\n{distribution_result}\n{eof_result}"
    else:
        return "No steganography detected."

# Just some test stuff
image_path = "encoded_image.png"
result = lsb_stego_detection(image_path)
print(result)
