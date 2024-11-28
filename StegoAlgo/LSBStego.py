from PIL import Image

def message_to_bin(message):
    return ''.join(format(ord(c), '08b') for c in message)

def encode_image(image_path, message, output_image_path):
    # Open the image
    image = Image.open(image_path)
    binary_message = message_to_bin(message) + '1111111111111110'  # Add an end of file marker at the end

    # Convert the image to a list of pixels
    pixels = image.load()
    width, height = image.size
    message_index = 0
    message_length = len(binary_message)

    # Iterate through all pixels and modify the LSB
    for y in range(height):
        for x in range(width):
            if message_index < message_length:
                pixel = list(pixels[x, y])  # Convert RGB to list to modify
                # Modify the LSB of each color channel (R, G, B)
                for i in range(3):  # Modify the R, G, and B channels
                    if message_index < message_length:
                        pixel[i] = pixel[i] & ~1 | int(binary_message[message_index])
                        message_index += 1
                pixels[x, y] = tuple(pixel)
            else:
                break

    # Save the new image
    image.save(output_image_path)
    print(f"Message encoded successfully in {output_image_path}")

def decode_image(image_path):
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size
    binary_message = ''

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for i in range(3):  # Check R, G, and B channels for LSB
                binary_message += str(pixel[i] & 1)

    # The binary message has an end of file marker
    end_marker = '1111111111111110'
    binary_message = binary_message[:binary_message.find(end_marker)]

    # Convert binary message back to string
    message = ''.join(chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8))

    return message

def read_message_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


image_path = 'Path_to_image/images/Surreal-World-Thumbnail.jpg'
message_file_path = 'Moby_Dick.txt'
message = read_message_from_file(message_file_path)

output_image_path = 'Path_to_stego/Stego Images/testing.png'

encode_image(image_path, message, output_image_path)

decoded_message = decode_image(output_image_path)
print("Decoded message:", decoded_message)
