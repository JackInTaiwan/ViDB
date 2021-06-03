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

# operation 1: delete_one_by_id
msg = {
    "request_type": "delete_one_by_id",
    "body": {
        "target_index": "a36eecce196245bbb40d17b8390e15c4"
    }
}

# operation 2: delete_one_by_id
# msg = {
#     "request_type": "delete_many_by_ids",
#     "body": {
#         "target_index_list": ["ed656edceb0248e5922926535d7a5dfb"]
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
