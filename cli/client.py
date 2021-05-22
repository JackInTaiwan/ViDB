import socket
import sys
import json


try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)

msg = {"request_type": "insert_one", "body": {"text": "Hello I'm Client."}}
str_ = json.dumps(msg)
byte_ = str_.encode()
encoded_msg = byte_
socket_.send(encoded_msg)
response = socket_.recv(1024)
str_ = response.decode()
decoded_res = json.loads(str_)
print(decoded_res)
socket_.close()
