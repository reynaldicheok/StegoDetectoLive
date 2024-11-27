import numpy as np
from PIL import Image
from io import BytesIO

def calculate_pixel_pair_difference(image_bytes: bytes):
    # Load image from bytes and greyscale it
    img = Image.open(BytesIO(image_bytes)).convert("L")
    img_array = np.array(img)

    height, width = img_array.shape
    differences = []
    for row in range(height):
        for col in range(width - 1):  # Avoid out-of-bound errors
            diff = abs(int(img_array[row, col]) - int(img_array[row, col + 1])) / 255.0
            differences.append(diff)
    return differences

def detect_stego(image_bytes: bytes, threshold: float):
    # Calculate pixel pair differences
    differences = calculate_pixel_pair_difference(image_bytes)

    # Count normalized differences exceeding the threshold
    anomalies = sum(1 for diff in differences if diff > threshold)

    # Metadata calculations
    total_pairs = len(differences)
    anomalies_percentage = (anomalies / total_pairs) * 100

    # Determine steganography presence
    is_stego = anomalies > total_pairs * 0.1

    metadata = {
        "total_pairs": total_pairs,
        "anomalies_count": anomalies,
        "anomalies_percentage": anomalies_percentage
    }

    return is_stego, metadata