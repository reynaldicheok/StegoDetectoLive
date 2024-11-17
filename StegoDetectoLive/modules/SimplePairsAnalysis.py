import numpy as np
from PIL import Image

def calculate_pixel_pair_difference(image):
    height, width = image.shape
    differences = []
    for row in range(height):
        for col in range(width - 1):  # Avoid out-of-bound errors
            diff = abs(int(image[row, col]) - int(image[row, col + 1])) / 255.0
            differences.append(diff)
    return differences

def detect_stego(image_path, threshold):
    # Load image and convert to grayscale
    img = Image.open(image_path).convert("L")
    img_array = np.array(img)

    # Calculate pixel pair differences
    differences = calculate_pixel_pair_difference(img_array)

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