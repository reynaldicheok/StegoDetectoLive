import os

from mitmproxy import http
import json
from StegoDetectoLive.modules.histogram import histogram

# Load the configuration file
with open("config.json", "r") as f:
    config = json.load(f)
    min_detections = config["min_detections"]

# Create a directory to store the images
if not os.path.exists("triage"):
    os.makedirs("triage")

def request(flow: http.HTTPFlow) -> None:
    print(flow.request.content)


def response(flow: http.HTTPFlow) -> None:
    isStego = histogram(flow.response.content)
    if isStego:
        print("Steganography detected")
        flow.kill()
    else:
        print("No steganography detected")


