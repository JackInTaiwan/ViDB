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

# operation 1: update_one_by_id
msg = {
    "request_type": "update_one_by_id",
    "body": {
        "target_index": "eae11acf55b0431093a00c2c3ec78ff",
        "metadata": {"tag_style": "style1"}
    }
}

# operation 2: update_many_by_ids
# msg = {
#     "request_type": "update_many_by_ids",
#     "body": {
#         "target_index_list": [
#             "eae11acf55b0431093a00c2c3ec78fff",
#             "ed6770d5140d42c1b621d7d0c9b28a06"
#         ],
#         "metadata_list": [
#             {"tag_style": "style1"},
#             {"tag_style": "style2"}
#         ]
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
