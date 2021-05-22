import os
import socketserver
import logging

from controller.controller import Controller
from setup.server import (
    setup_config,
    setup_logging,
    setup_msg_converter,
    setup_operation,
)

OPERATION = {}



if __name__ == "__main__":
    # Set up the configuration
    setup_config()

    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Set up the operations
    setup_operation()

    # Set up the server
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    msg_converter = setup_msg_converter(os.getenv("converter.model"))
    Controller.msg_converter = msg_converter
    
    server = socketserver.ThreadingTCPServer((os.getenv("connection.host"), int(os.getenv("connection.port"))), Controller)

    logger.info("The server is initiated with its host={} and port={}."
        .format(os.getenv("connection.host"), os.getenv("connection.port"))) 

    # Run the servier
    server.serve_forever()
