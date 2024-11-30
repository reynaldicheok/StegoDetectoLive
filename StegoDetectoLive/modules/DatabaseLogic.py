import os
import sqlite3
from PIL import Image
import imagehash
from scipy.spatial import distance
import io

from modules.database_generation import database_generation


def hammingdistance(a, b):
    a_res = imagehash.hex_to_hash(a)
    b_res = imagehash.hex_to_hash(b)
    hammingDist = distance.hamming(a_res.hash.flatten(), b_res.hash.flatten())
    return hammingDist


def getSimilarImages(image: bytes) -> str:
    conn = sqlite3.connect('images.db')
    conn.create_function("hammingdistance", 2, hammingdistance)

    c = conn.cursor()
    phash = str(imagehash.phash(Image.open(io.BytesIO(image))))
    c.execute("SELECT path FROM images WHERE hammingdistance(phash, ?) < 0.1", (phash,))
    result = c.fetchall()
    conn.close()
    if len(result) == 0:
        return None
    return result[0][0]

if not os.path.exists("images.db"):
    database_generation()