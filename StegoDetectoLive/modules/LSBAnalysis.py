from io import BytesIO
from PIL import Image
import numpy as np
from scipy.stats import entropy
import re

def get_lsb(image: bytes):
    img = Image.open(BytesIO(image))
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

def extract_text_from_lsb(lsb_values, eof_marker):
    # Convert the LSB values into a binary string
    binary_message = ''.join(map(str, lsb_values))

    # Find where the EOF marker occurs in the binary stream
    end_index = binary_message.find(eof_marker)

    # If we can't find the EOF marker, there is no message
    if end_index == -1:
        return None

    # Trim the binary message to remove the EOF marker and everything after it also check for the past 16 characters
    start_index = end_index - 128
    binary_message = binary_message[start_index:end_index]

    # Convert the binary message back to characters (bytes)
    binary_message = binary_message[:len(binary_message) // 8 * 8]

    # Split the binary string into chunks of 8 bits (1 byte each)
    byte_list = [binary_message[i:i + 8] for i in range(0, len(binary_message), 8)]

    # Convert each byte into a character
    decoded_message = ''
    for byte in byte_list:
        decoded_message += chr(int(byte, 2))

    # Use regex to check if the message contains garbage
    if is_message_valid(decoded_message):
        return decoded_message
    else:
        return None  # Return None if the message is not valid

def is_message_valid(message):
    # Use regex to check for non-ASCII characters if there is then its probably garbage
    if re.search(r'[^\x00-\x7F]', message):
        return False
    else:
        return True

def lsb_stego_detection(image: bytes):
    # Extract the LSBs from the image
    lsb_values = get_lsb(image)

    # Analyze the LSBs to detect any hidden data
    lsb_entropy, entropy_label = analyze_lsb(lsb_values)
    proportion_zero, proportion_one, distribution_label = analyze_lsb_distribution(lsb_values)
    eof_stego, eof_marker_used = check_eof_marker(lsb_values)
    # If an EOF marker was found, extract the LSBs before it
    if eof_stego:
        extracted_text = extract_text_from_lsb(lsb_values, eof_marker_used)

        if extracted_text:
            # If extracted text is meaningful words, we flag it as steganography
            eof_stego = True
        else:
            # Else do not flag it as steganography if it's random garbage
            extracted_text = "Random Garbage"
            eof_stego = False

    metadata = {
        "entropy": lsb_entropy,
        "entropy_label": entropy_label,
        "proportion_zero": proportion_zero,
        "proportion_one": proportion_one,
        "distribution_label": distribution_label,
        "eof_marker_detected": eof_stego,
        "eof_marker_used": eof_marker_used,
        "extract_text": extracted_text
    }

    # Combine all detection results to determine if steganography is present
    is_steganography = entropy_label == "Low" or distribution_label == "Skewed" or eof_stego

    return is_steganography, metadata