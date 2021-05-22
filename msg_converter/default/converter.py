import os
import json

from .util import catch_error
from msg_converter.base import BaseConveter



class Converter(BaseConveter):
    def __init__(self):
        self.encoding = os.getenv("msg_converter.encoding")

    
    def encode(self, decoded_msg, encoding=None):
        return self.dict_to_byte(decoded_msg, encoding)

    
    def decode(self, encoded_msg, encoding=None):
        return self.byte_to_dict(encoded_msg, encoding)


    @catch_error
    def parse(self, msg):
        return {
            "request_type": msg["request_type"],
            "body": msg["body"]
        }
    
    @catch_error
    def dict_to_byte(self, dict_, encoding):
        encoding = encoding or self.encoding
        str_ = json.dumps(dict_)
        # binary = " ".join(format(ord(letter), "b") for letter in str_)
        byte_ = str_.encode(encoding=encoding, errors="strict")

        return byte_

    @catch_error
    def byte_to_dict(self, byte_, encoding):
        encoding = encoding or self.encoding
        str_ = byte_.decode(encoding=encoding, errors="strict")
        dict_ = json.loads(str_)  

        return dict_
