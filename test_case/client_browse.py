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
    "request_type": "browse_by_random",
    "body": {
        "num_inst": 10
    }
}

# msg = {
#     "request_type": "browse_by_cluster",
#     "body": {
#         "num_inst": 10
#     }
# }


### Encode the message
str_ = json.dumps(msg)
byte_ = str_.encode()
encoded_msg = byte_

socket_.send(encoded_msg)

str_ = ""
while response:=socket_.recv(1024):
    str_ += response.decode()


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

socket_.close()