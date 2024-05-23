import logging
import os
import signal
import sys
from concurrent import futures

import grpc
from loguru import logger

from user.handlers.user import UserService
from user.proto import user_pb2_grpc

# BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# sys.path.append(BASE_DIR)

def on_exit(signo, frame):
    logger.info("Shutting down server...")
    sys.exit(0)


def serve():
    # logger.add("logs/user_server_{time}.log")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')

    # 主进程退出信号监听
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    logger.info("Starting server. Listening on port 50051.")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
