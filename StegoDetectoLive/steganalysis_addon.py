import os
from datetime import datetime
from mitmproxy import http
import json
from requests_toolbelt.multipart import decoder
from StegoDetectoLive.modules.LSBAnalysis import lsb_stego_detection
from StegoDetectoLive.modules.histogram import histogram
import pyfsig

# Load the configuration file
with open("config.json", "r") as f:
    config = json.load(f)
    min_detections = config["min_detections"]
    allow_all_traffic_and_save_data = config["allow_all_traffic_and_save_data"]
    print(min_detections)
    print(allow_all_traffic_and_save_data)

# Create a directory to store the images
if not os.path.exists("triage"):
    os.makedirs("triage")

img_types_list = ["png", "jpg", "jpeg"]


def request(flow: http.HTTPFlow) -> None:
    # For multipart/form-data requests
    if b"Content-Type" in flow.request.headers and "multipart/form-data" in flow.request.headers[b"Content-Type"]:
        try:
            to_kill = False
            multipart_data = decoder.MultipartDecoder(flow.request.content, flow.request.headers["Content-Type"])
            for part in multipart_data.parts:
                fileBytes = part.content[:128]
                fileTypes = pyfsig.find_matches_for_file_header(file_header=fileBytes)
                isImage = False
                fileExtension = None
                for fileType in fileTypes:
                    if fileType.file_extension in img_types_list:
                        isImage = True
                        fileExtension = fileType.file_extension
                        break
                if isImage:
                    to_kill = check_Stego(part.content, fileExtension)
            if to_kill:
                flow.kill()
        except Exception as e:
            print("Content type is not multipart/form-data")
            flow.kill()
    # else inspect the contents for images
    else:
        fileBytes = flow.request.content[:128]
        fileTypes = pyfsig.find_matches_for_file_header(file_header=fileBytes)
        isImage = False
        fileExtension = None
        for fileType in fileTypes:
            if fileType.file_extension in img_types_list:
                isImage = True
                fileExtension = fileType.file_extension
                break
        if isImage:
            to_kill = check_Stego(flow.request.content, fileExtension)
            if to_kill:
                flow.kill()


def response(flow: http.HTTPFlow) -> None:
    # inspect the contents for images
    fileBytes = flow.response.content[:128]
    fileTypes = pyfsig.find_matches_for_file_header(file_header=fileBytes)
    isImage = False
    fileExtension = None
    for fileType in fileTypes:
        if fileType.file_extension in img_types_list:
            isImage = True
            fileExtension = fileType.file_extension
            break

    if isImage:
        to_kill = check_Stego(flow.response.content, fileExtension)
        if to_kill:
            flow.kill()
            return


def check_Stego(data, fileExtension):
    isStegoList = []
    stegoMetadata = {}
    # Check if the image is steganography
    # LSB
    lsbIsStego, lsbMetadata = lsb_stego_detection(data)
    isStegoList.append(lsbIsStego)
    stegoMetadata["LSB"] = lsbMetadata

    # Histogram
    histogramIsStego = histogram(data)
    isStegoList.append(histogramIsStego)

    detections = isStegoList.count(True)
    if detections >= min_detections:
        # Save the image to the triage folder
        with open("triage/{}.{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), fileExtension), "wb") as f:
            f.write(data)
        # Save the metadata to the triage folder
        with open("triage/{}.json".format(datetime.now().strftime("%Y%m%d%H%M%S")), "w") as f:
            json.dump(stegoMetadata, f, indent=4)
        if not allow_all_traffic_and_save_data:
            return True
    return False
