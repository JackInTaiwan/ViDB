import socket
import sys
import json


try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)

msg = {
    "request_type": "insert_one_by_path",
    "body": {
        "image_path": "/home/jack/Downloads/test/t1.jpg",
        "metadata": {}
    }
}

# msg = {
#     "request_type": "insert_many_by_dir",
#     "body": {
#         "image_fold_dir": "/home/jack/Downloads/test",
#         "metadata": {}
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
