import os
import socketserver
import logging

from controller.controller import Controller
from setup.server import (
    setup_config,
    setup_logging,
    setup_msg_resolver,
    setup_operation,
    setup_storage_engine,
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

    # Set up the message resolver
    msg_resolver = setup_msg_resolver(os.getenv("resolver.model"))

    # Set up the storage engine
    storage_engine = setup_storage_engine(os.getenv("resolver.model"))

    # Set up the server
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    
    Controller.msg_resolver = msg_resolver
    Controller.storage_engine = storage_engine
    
    server = socketserver.ThreadingTCPServer((os.getenv("connection.host"), int(os.getenv("connection.port"))), Controller)

    logger.info("The server is initiated with its host={} and port={}."
        .format(os.getenv("connection.host"), os.getenv("connection.port"))) 

    # Run the servier
    server.serve_forever()
