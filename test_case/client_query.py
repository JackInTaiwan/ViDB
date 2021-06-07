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



# operation 1: query_nearest_by_content
def query_nearest_by_content():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_nearest_by_content",
        "body": {
            "target_index": target_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 2: query_nearest_by_style
def query_nearest_by_style():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_nearest_by_style",
        "body": {
            "target_index": target_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 3: query_farthest_by_content
def query_farthest_by_content():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_farthest_by_content",
        "body": {
            "target_index": target_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 4: query_farthest_by_style
def query_farthest_by_style():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_farthest_by_style",
        "body": {
            "target_index": target_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 5: query_by_tag_all
def query_by_tag_all():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    tags =  ["cartoon", "elephant"]
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_by_tag_all",
        "body": {
            "target_index": target_index,
            "tags": tags,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }
    return msg


# operation 6: query_by_tag_partial
def query_by_tag_partial():
    target_index = "5a45fa990fd0410e9843f30fad365054"
    tags =  ["cartoon", "elephant"]
    num_inst = 10
    return_origin_size = False

    msg = {
        "request_type": "query_by_tag_partial",
        "body": {
            "target_index": target_index,
            "tags": tags,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 7: query_range_by_content
def query_range_by_content():
    group_index = [
        "5a45fa990fd0410e9843f30fad365054",
        "5a45fa990fd0410e9843f30fad365054",
        "5a45fa990fd0410e9843f30fad365054"
    ]
    num_inst = 5
    return_origin_size = False

    msg = {
        "request_type": "query_range_by_content",
        "body": {
            "group_index": group_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg


# operation 8: query_range_by_style
def query_range_by_style():
    group_index = [
        "5a45fa990fd0410e9843f30fad365054",
        "fd9c7e118e4b404497fe76249f44f341",
        "5a45fa990fd0410e9843f30fad365054"
    ]
    num_inst = 5
    return_origin_size = False

    msg = {
        "request_type": "query_range_by_style",
        "body": {
            "group_index": group_index,
            "num_inst": num_inst,
            "return_origin_size": return_origin_size
        }
    }

    return msg



if __name__ == "__main__":
    OPERATION_TABLE = {
        "query_nearest_by_content": query_nearest_by_content,
        "query_nearest_by_style": query_nearest_by_style,
        "query_farthest_by_content": query_farthest_by_content,
        "query_farthest_by_style": query_farthest_by_style,
        "query_by_tag_all": query_by_tag_all,
        "query_by_tag_partial": query_by_tag_partial,
        "query_range_by_content": query_range_by_content,
        "query_range_by_style": query_range_by_style
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
        image_base64 = v
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        image_array = np.array(image)
        cv2.namedWindow(k)
        cv2.moveWindow(k, 500, 500) 
        cv2.imshow(k, image_array)
        cv2.waitKey(0)
        cv2.destroyWindow(k)
