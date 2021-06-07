import socket
import os
import sys
import json
import base64


try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)


### Insert all the images in "./data/example"
# image_dir = "./data/example/"
#image_dir = "./data/test/images"
#image_files = sorted(os.listdir(image_dir))
#image_dir = "./data/example/"
#image_files = sorted(os.listdir("../data/example/"))

# Create metadata
'''
metadata = {}
for file in image_files:
    s = file.split("_")
    tag_content = s[-2]
    tag_style = "_".join(s[:-2])
    metadata[file] = {"tag_content": tag_content, "tag_style": tag_style}
'''

# operation 1: insert_many_by_dir
'''
msg = {
    "request_type": "insert_many_by_dir",
    "body": {
        "image_fold_dir": image_dir,
        "metadata": metadata
    }
}
'''

# operation 2: insert_one_by_path
# msg = {
#     "request_type": "insert_one_by_path",
#     "body": {
#         "image_path": "/home/jack/Downloads/test/t1.jpg",
#         "metadata": {}
#     }
# }

# operation 3: insert_one_by_byte

txt_path = "../data/test/bytes/art_painting_dog_030.txt"
with open(txt_path, 'rb') as myfile:
    image_bytes=myfile.read()

meta_path = "../data/test/singleimg_meta.json"
f = open(meta_path, "r")
metaData = json.load(f)

msg = {
    "request_type": "insert_one_by_byte",
    "body": {
        "bytes": base64.b64encode(image_bytes).decode(),
        "metadata": metaData
    }
}

# operation 4: insert_many_by_byte
'''
bytes_list = []
bytes_dir = "../data/test/bytes"
txt_file_list = sorted(os.listdir(bytes_dir))
for txt in txt_file_list:
    with open(txt, 'rb') as myfile:
        bytes_list.append(myfile.read())

meta_path = "../data/test/metaData_bytes.json"
f = open(meta_path, "r")
metaData = json.load(f)

msg = {
    "request_type": "insert_many_by_byte",
    "body": {
        "bytes_list": bytes_list,
        "metadata": metaData
    }
}
'''



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
