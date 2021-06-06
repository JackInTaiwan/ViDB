import io
import os
import sys
import json
import base64
import socket
import cv2
import numpy as np

from PIL import Image



try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)



# operation 1: query_nearest_by_content
msg = {
    "request_type": "query_nearest_by_content",
    "body": {
        "target_index": "8ea87d42f06444c5a809a620f9efcbdc",
        "num_inst": 10,
        "return_origin_size": False
    }
}

# operation 2: query_nearest_by_style
# msg = {
#     "request_type": "query_nearest_by_style",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "return_origin_size": False
#     }
# }

# operation 3: query_farthest_by_content
# msg = {
#     "request_type": "query_farthest_by_content",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "return_origin_size": False
#     }
# }

# operation 4: query_farthest_by_style
# msg = {
#     "request_type": "query_farthest_by_style",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "return_origin_size": False
#     }
# }

# operation 5: query_by_tag_all
# msg = {
#     "request_type": "query_by_tag_all",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "tags": ["cartoon", "elephant"],
#         "return_origin_size": False
#     }
# }

# operation 6: query_by_tag_partial
# msg = {
#     "request_type": "query_by_tag_partial",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "tags": ["cartoon", "elephant"],
#         "return_origin_size": False
#     }
# }

# operation 7: query_range_by_content
# msg = {
#     "request_type": "query_range_by_content",
#     "body": {
#         "group_index": [
#             "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#             "a0ac227a9c56489cb50418ff44007f18",
#             "d5d0dfa498924a44b4fc4abb27c53a52"
#         ],
#         "num_inst": 5,
#         "return_origin_size": False
#     }
# }

# operation 8: query_range_by_style
# msg = {
#     "request_type": "query_range_by_style",
#     "body": {
#         "group_index": [
#             "a8d0e0e2a2da4c2e92ed458a21e3ceb3",
#             "c98337e6490741a9a0e1691f4ff7e5e2",
#             "687e20ece9fe44568643f5bcb958a680"
#         ],
#         "num_inst": 5,
#         "return_origin_size": False
#     }
# }


### Encode the message
str_ = json.dumps(msg)
byte_ = str_.encode()
encoded_msg = byte_

socket_.send(encoded_msg)


### Receive the response
str_ = ""
while response:=socket_.recv(1024):
    str_ += response.decode()
socket_.close()


### Decode the message
decoded_res = json.loads(str_)


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
