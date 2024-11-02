import sqlite3
import os
import imagehash
from PIL import Image

conn = sqlite3.connect('images.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS images (path text, phash text)''')

image_folder = 'images'
image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
image_paths = sorted(image_paths)

for image_path in image_paths:
    phash = str(imagehash.phash(Image.open(image_path)))
    c.execute("INSERT INTO images VALUES (?, ?)", (image_path, phash))

conn.commit()
conn.close()

print("Database generation complete")

