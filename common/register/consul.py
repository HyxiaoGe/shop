import requests

from common.register import base
import consul


class ConsulRegister(base.Register):
    def register(self, name, id, address, port, tags, check) -> bool:
        if check is None:
            check = {
                "GRPC": f"{address}:{port}",
                "GRPCUseTLS": False,
                "Timeout": "5s",
                "Interval": "5s",
                "DeregisterCriticalServiceAfter": "15s"
            }
        return self.c.agent.service.register(name=name, service_id=id, address=address, port=port, tags=tags, check=check)

    def deRegister(self):
        return self.c.agent.service.deregister("user")

    def get_all_services(self):
        return self.c.agent.services()

    def filter_services(self, filter):
        url = f"http://{self.host}:{self.port}/v1/agent/services"
        params = {
            "filter": filter
        }
        return requests.get(url, params=params).json()

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = consul.Consul(host=self.host, port=self.port)
