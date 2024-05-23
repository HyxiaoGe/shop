from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


# 使用peewee的连接池，继承ReconnectMixin，实现自动重连
class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


DB = ReconnectMySQLDatabase('shop_user', user='root', password='hyxiao', host='127.0.0.1', max_connections=8)