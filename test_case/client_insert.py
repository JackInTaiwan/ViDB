import os
import sys
import json
import socket
import base64

from argparse import ArgumentParser



try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)



# operation 1: insert_one_by_path
def insert_one_by_path():
    meta_path = "./data/test/singleimg_meta.json"
    image_path = "./data/test/images/art_painting_dog_030.jpg"

    with open(meta_path, "r") as f:
        metaData = json.load(f)

    msg = {
        "request_type": "insert_one_by_path",
        "body": {
            "image_path": image_path,
            "metadata": metaData
        }
    }

    return msg


# operation 2: insert_many_by_dir
def insert_many_by_dir():
    image_dir = "./data/example/"

    image_files = sorted(os.listdir(image_dir))
    metadata = {}

    for fn in image_files:
        s = fn.split("_")
        tag_content = s[-2]
        tag_style = "_".join(s[:-2])
        metadata[fn] = {"tag_content": tag_content, "tag_style": tag_style}

    msg = {
        "request_type": "insert_many_by_dir",
        "body": {
            "image_fold_dir": image_dir,
            "metadata": metadata
        }
    }

    return msg


# operation 3: insert_one_by_byte
def insert_one_by_byte():
    txt_path = "./data/test/bytes/art_painting_dog_030.txt"
    meta_path = "./data/test/singleimg_meta.json"

    with open(txt_path, "rb") as f:
        image_bytes = f.read()

    with open(meta_path) as f:
        metadata = json.load(f)

    msg = {
        "request_type": "insert_one_by_byte",
        "body": {
            "bytes": base64.b64encode(image_bytes).decode(),
            "metadata": metadata
        }
    }

    return msg


# operation 4: insert_many_by_byte
def insert_many_by_byte():
    bytes_dir = "./data/test/bytes"
    meta_path = "./data/test/metaData_bytes.json"

    txt_file_list = sorted(os.listdir(bytes_dir))
    bytes_list = []

    for txt in txt_file_list:
        path = os.path.join(bytes_dir, txt)
        with open(path, "rb") as f:
            bytes_list.append(base64.b64encode(f.read()).decode())

    with open(meta_path) as f:
        metadata = json.load(f)

    msg = {
        "request_type": "insert_many_by_byte",
        "body": {
            "bytes_list": bytes_list,
            "metadata": metadata
        }
    }

    return msg



if __name__ == "__main__":
    OPERATION_TABLE = {
        "insert_one_by_path": insert_one_by_path,
        "insert_many_by_dir": insert_many_by_dir,
        "insert_one_by_byte": insert_one_by_byte,
        "insert_many_by_byte": insert_many_by_byte
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

    ### Send and receive the request
    socket_.send(encoded_msg)
    response = socket_.recv(100000)
    socket_.close()
    str_ = response.decode()

    ### Decode the message
    decoded_res = json.loads(str_)
    print(decoded_res)
