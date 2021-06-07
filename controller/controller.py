import os
import logging
import socketserver

from operation import OPERATION
from variable import (
    error_msg as EM,
    operation as OP,
)

logger = logging.getLogger(__name__)



class Controller(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.max_reception_byte = int(os.getenv("connection.max_reception_byte"))
        self.msg_resolver = Controller.msg_resolver
        self.storage_engine = Controller.storage_engine

        super().__init__(*args, **kwargs)
        

    def handle(self):
        try:
            msg = bytes()
            decoded_msg = None

            while msg_ := self.request.recv(self.max_reception_byte):
                msg += msg_
                decoded_msg = self.msg_resolver.decode(msg)
                if decoded_msg: break

            data = self.msg_resolver.parse(decoded_msg)

            if not data:
                response = {"success": False, "error_msg": EM.CANNOT_PARSE_MSG_BODY}
                encoded_response = self.msg_resolver.encode(response)
                self.request.send(encoded_response)

            result = OPERATION[data["request_type"]](body=data["body"], storage_engine=self.storage_engine)
            encoded_result = self.msg_resolver.encode(result)
            
            # Send the result back
            self.request.send(encoded_result)
            logger.info("[request_type: {}] [status: success] [byte: {}]".format(data["request_type"], len(msg)))

        finally:
            # Close the session
            self.request.close()