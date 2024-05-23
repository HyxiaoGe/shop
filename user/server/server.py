import logging
from concurrent import futures

import grpc

from user.proto import user_pb2_grpc
from user.handlers.user import UserService


def sever():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    print('Starting server. Listening on port 50051.')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    sever()
