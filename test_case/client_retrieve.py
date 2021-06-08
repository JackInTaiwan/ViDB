import io
import os
import sys
import json
import base64
import socket
import cv2
import numpy as np

from argparse import ArgumentParser
from PIL import Image


try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)



# operation 1: retrieve_one
def retrieve_one():
    target_index = "d4e2d2fefdab449d90f41c7ad2daee04"

    msg = {
        "request_type": "retrieve_one",
        "body": {
            "target_index": target_index,
            "return_origin_size": True
        }
    }

    return msg


# operation 2: retrieve_many
def retrieve_many():
    target_index_list = [
        "e4cc91d6d64f4307bebf36e422a63c51",
        "d4e2d2fefdab449d90f41c7ad2daee04"
    ]

    msg = {
        "request_type": "retrieve_many",
        "body": {
            "target_index_list": target_index_list,
            "return_origin_size": True
        }
    }

    return msg



if __name__ == "__main__":
    OPERATION_TABLE = {
        "retrieve_one": retrieve_one,
        "retrieve_many": retrieve_many
    }
    parser = ArgumentParser()
    parser.add_argument(
        "--operation", "-o",
        help="specified operation",
        required=True,
        choices=OPERATION_TABLE.keys()
    )
    args = parser.parse_args()

    ### Encode the message
    msg = OPERATION_TABLE[args.operation]()
    str_ = json.dumps(msg)
    byte_ = str_.encode()
    encoded_msg = byte_

    ### Send and receive the response
    socket_.send(encoded_msg)
    str_ = ""
    while response:=socket_.recv(1024):
        str_ += response.decode()
    socket_.close()

    ### Decode the message
    decoded_res = json.loads(str_)
    print(decoded_res["success"])

    ### Present the thumbnails
    for k, v in decoded_res["body"].items():
        image_base64 = v["image"]
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        image_array = np.array(image)
        cv2.namedWindow(k)
        cv2.moveWindow(k, 500, 500) 
        cv2.imshow(k, image_array)
        cv2.waitKey(0)
        cv2.destroyWindow(k)