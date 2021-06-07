import os
import sys
import json
import socket

from argparse import ArgumentParser



try:
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect(("0.0.0.0", 10000))
except socket.error as error:
    sys.stderr.write(str(error))
    exit(1)



# operation 1: update_one_by_id
def update_one_by_id():
    target_index = "2def7ca1d52140148fd8d56adb79026c"
    new_metadata = {"tag_style": "style1"}

    msg = {
        "request_type": "update_one_by_id",
        "body": {
            "target_index": target_index,
            "metadata": new_metadata
        }
    }

    return msg


# operation 2: update_many_by_ids
def update_many_by_ids():
    target_index_list = [
        "7394efeeef194d1eb3c1c975f1d06e4f"
    ]

    new_metadata_list = [
        {"tag_style": "style1"}
    ]

    msg = {
        "request_type": "update_many_by_ids",
        "body": {
            "target_index_list": target_index_list,
            "metadata_list": new_metadata_list
        }
    }

    return msg



if __name__ == "__main__":
    OPERATION_TABLE = {
        "update_one_by_id": update_one_by_id,
        "update_many_by_ids": update_many_by_ids
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
    response = socket_.recv(1024)
    socket_.close()
    str_ = response.decode()

    ### Decode the message
    decoded_res = json.loads(str_)
    print(decoded_res)
