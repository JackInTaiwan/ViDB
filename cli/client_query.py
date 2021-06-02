import socket
import os
import sys
import json


try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)

msg = {
    "request_type": "query_nearest_by_content",
    "body": {
        "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
        "num_inst": 10
    }
}

# msg = {
#     "request_type": "query_nearest_by_style",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10
#     }
# }

# msg = {
#     "request_type": "query_farthest_by_content",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10
#     }
# }

# msg = {
#     "request_type": "query_farthest_by_style",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10
#     }
# }

# msg = {
#     "request_type": "query_by_tag_all",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "tags": ["cartoon", "elephant"]
#     }
# }

# msg = {
#     "request_type": "query_by_tag_partial",
#     "body": {
#         "target_index": "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#         "num_inst": 10,
#         "tags": ["cartoon", "elephant"]
#     }
# }

# msg = {
#     "request_type": "query_range_by_content",
#     "body": {
#         "group_index": [
#             "4ccd7b8fbe0d44efba4c53e37c3b9a45",
#             "a0ac227a9c56489cb50418ff44007f18",
#             "d5d0dfa498924a44b4fc4abb27c53a52"
#         ],
#         "num_inst": 5
#     }
# }

# msg = {
#     "request_type": "query_range_by_style",
#     "body": {
#         "group_index": [
#             "a8d0e0e2a2da4c2e92ed458a21e3ceb3",
#             "c98337e6490741a9a0e1691f4ff7e5e2",
#             "687e20ece9fe44568643f5bcb958a680"
#         ],
#         "num_inst": 5
#     }
# }

### Encode the message
str_ = json.dumps(msg)
byte_ = str_.encode()
encoded_msg = byte_

socket_.send(encoded_msg)
response = socket_.recv(1024)
str_ = response.decode()

### Decode the message
decoded_res = json.loads(str_)
print(decoded_res)

socket_.close()
