import os
import logging
import socketserver
import time

from operation import OPERATION
from variable import (
    error_msg as EM,
    operation as OP,
)

logger = logging.getLogger(__name__)



def clock(func):
    def clocked(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        run_time = time.time() - start
        return res, run_time

    return clocked
    


class Controller(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.max_reception_byte = int(os.getenv("connection.max_reception_byte"))
        self.msg_resolver = Controller.msg_resolver
        self.storage_engine = Controller.storage_engine
        self.cache = Controller.cache

        super().__init__(*args, **kwargs)
    

    @clock
    def run_operation(self, request_type, body):
        result = OPERATION[request_type](
            body=body,
            storage_engine=self.storage_engine,
            cache = self.cache
        )

        return result


    def handle(self):
        try:
            msg = bytes()
            decoded_msg = None

            while msg_ := self.request.recv(self.max_reception_byte):
                msg += msg_
                decoded_msg = self.msg_resolver.dry_decode(msg)
                if decoded_msg: break

            data = self.msg_resolver.parse(decoded_msg)

            if not data:
                result = {"success": False, "error_msg": EM.CANNOT_PARSE_MSG_BODY}
                response = self.msg_resolver.encode(result)
                self.request.send(response)

            result, run_time = self.run_operation(data["request_type"], data["body"])
            response = self.msg_resolver.encode(result)
            
            # Send the result back
            self.request.send(response)
            logger.info(
                "[request_type: {}] [status: {}] [run_time: {}]"
                .format(
                    data["request_type"],
                    "success" if result["success"] else "fail",
                    round(run_time, 7)
                )
            )

        finally:
            # Close the session
            self.request.close()