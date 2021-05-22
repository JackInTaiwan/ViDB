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
        self.msg_converter = Controller.msg_converter
        super().__init__(*args, **kwargs)
        

        
    def handle(self):
        try:
            msg = self.request.recv(self.max_reception_byte+1)
            
            if len(msg) > self.max_reception_byte:
                response = {"success": False, "error_msg": EM.EXCEL_MAX_RECEPTION_BYTE}
                encoded_response = self.msg_converter.encode(response)
                self.request.send(encoded_response)
            else:
                decoded_msg = self.msg_converter.decode(msg)
                data = self.msg_converter.parse(decoded_msg)

                if not data:
                    # TODO
                    pass

                result = OPERATION[data["request_type"]](data["body"])

                encoded_result = self.msg_converter.encode(result)
                
                # Send the result back
                self.request.send(encoded_result)
                logger.info("[request_type: {}] [status: success] [byte: {}]".format(data["request_type"], len(msg)))

        finally:
            # Close the session
            self.request.close()