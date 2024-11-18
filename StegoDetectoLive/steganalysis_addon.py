import os
from datetime import datetime

from mitmproxy import http
import json

from StegoDetectoLive.modules.LSBAnalysis import lsb_stego_detection
from StegoDetectoLive.modules.histogram import histogram

# Load the configuration file
with open("config.json", "r") as f:
    config = json.load(f)
    min_detections = config["min_detections"]
    allow_all_traffic_and_save_data = config["allow_all_traffic_and_save_data"]

# Create a directory to store the images
if not os.path.exists("triage"):
    os.makedirs("triage")

def request(flow: http.HTTPFlow) -> None:
    print(flow.request.content)


def response(flow: http.HTTPFlow) -> None:
    isStego = []
    isStego.append(histogram(flow.response.content))
    lsbMetadata, lsbIsStego = lsb_stego_detection(flow.response.content)
    isStego.append(lsbIsStego)
    detections = isStego.count(True)
    
    if detections >= min_detections:
        print("Steganography detected")
        # Make a new folder in the triage directory with timestamp of current time
        timestamp = str(datetime.datetime.now())
        os.makedirs("triage/" + timestamp)
        # Save the image in the new folder with the timestamp as the filename
        with open("triage/" + timestamp + "/" + timestamp + ".png", "wb") as f:
            f.write(flow.response.content)
        flow.kill()
    else:
        print("No steganography detected")


