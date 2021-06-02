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


### Insert all the images in "./data/example"
image_dir = "./data/example/"
image_files = sorted(os.listdir(image_dir))

# Create metadata
metadata = {}
for file in image_files:
    s = file.split("_")
    tag_content = s[-2]
    tag_style = "_".join(s[:-2])
    metadata[file] = {"tag_content": tag_content, "tag_style": tag_style}

msg = {
    "request_type": "insert_many_by_dir",
    "body": {
        "image_fold_dir": image_dir,
        "metadata": metadata
    }
}


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