import os
from datetime import datetime
from mitmproxy import http
import json
from requests_toolbelt.multipart import decoder
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
    # Block all images requests
    if b"Content-Type" in flow.request.headers and "image" in flow.request.headers[b"Content-Type"]:
        to_kill = check_Stego(flow.request.content)
        if to_kill:
            flow.kill()

    if b"Content-Type" in flow.request.headers and "multipart/form-data" in flow.request.headers[b"Content-Type"]:
        to_kill = False
        multipart_data = decoder.MultipartDecoder(flow.request.content, flow.request.headers["Content-Type"])
        for part in multipart_data.parts:
            try:
                to_kill = check_Stego(part.content)
            except Exception as e:
                print("Not an image")
        if to_kill:
            flow.kill()


def response(flow: http.HTTPFlow) -> None:
    # Block all images responses
    # Check if the response headers contain "Content-Type"
    if b"Content-Type" in flow.response.headers and "image" in flow.response.headers[b"Content-Type"]:
        to_kill = check_Stego(flow.response.content)
        if to_kill:
            flow.kill()


def check_Stego(data):
    isStegoList = []
    # Check if the image is steganography
    lsbIsStego, lsbMetadata = lsb_stego_detection(data)
    isStegoList.append(lsbIsStego)

    histogramIsStego = histogram(data)
    isStegoList.append(histogramIsStego)
    detections = isStegoList.count(True)
    if detections >= min_detections or allow_all_traffic_and_save_data:
        print("Steganography image detected")
        # Save the image to the triage folder
        with open("triage/{}.png".format(datetime.now().strftime("%Y%m%d%H%M%S")), "wb") as f:
            f.write(data)
        # Save the metadata to the triage folder
        with open("triage/{}.json".format(datetime.now().strftime("%Y%m%d%H%M%S")), "w") as f:
            json.dump(lsbMetadata, f)
        if not allow_all_traffic_and_save_data:
            return True
    return False
