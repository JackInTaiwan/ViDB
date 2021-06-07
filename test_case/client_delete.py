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



# operation 1: delete_one_by_id
def delete_one_by_id():
    target_index = "122e233586a14c6799ea7d83ea941a03"

    msg = {
        "request_type": "delete_one_by_id",
        "body": {
            "target_index": target_index
        }
    }

    return msg


# operation 2: delete_many_by_ids
def delete_many_by_ids():
    target_index_list = ["06920bfcc36e4ce3b7710a5598df8b13"]

    msg = {
        "request_type": "delete_many_by_ids",
        "body": {
            "target_index_list": target_index_list
        }
    }

    return msg


# operation 3: delete_all_data
def delete_all_data():
    msg = {
        "request_type": "delete_all",
        "body": {}
    }

    return msg



if __name__ == "__main__":
    OPERATION_TABLE = {
        "delete_one_by_id": delete_one_by_id,
        "delete_many_by_ids": delete_many_by_ids,
        "delete_all_data": delete_all_data
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
