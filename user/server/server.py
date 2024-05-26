import logging
import signal
import sys
import argparse
import socket
from concurrent import futures

import grpc
from loguru import logger

from common.grpc_health.v1 import health_pb2_grpc, health
from user.handlers.user import UserService
from user.proto import user_pb2_grpc
from common.register import consul
from user.settings import settings


# BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# sys.path.append(BASE_DIR)

def on_exit(signo, frame):
    logger.info("Shutting down server...")
    sys.exit(0)


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port


def serve():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip',
                        nargs="?",
                        type=str,
                        default=settings.CONSUL_HOST,
                        help="binding ip"
                        )
    parser.add_argument('--port',
                        nargs="?",
                        type=int,
                        default=0,
                        help="the listening port"
                        )
    args = parser.parse_args()

    if args.port == 0:
        port = get_free_tcp_port()
    else:
        port = args.port

    # logger.add("logs/user_server_{time}.log")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 注册用户服务
    user_pb2_grpc.add_UserServicer_to_server(UserService(), server)
    # 注册健康检查服务
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    server.add_insecure_port('[::]:50051')

    # 主进程退出信号监听
    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    logger.info("Starting server. Listening on port 50051.")
    server.start()

    logger.info(f"服务注册开始")
    register = consul.ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)
    if not register.register(name=settings.SERVICE_NAME, id=settings.SERVICE_NAME, address=settings.NGROK_ADDRESS, port=settings.NGROK_PORT, tags=settings.SERVICE_TAGS, check=None):
        logger.info(f"服务注册失败")
        sys.exit(0)
    logger.info(f"服务注册成功")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()