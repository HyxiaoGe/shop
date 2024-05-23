from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


# 使用peewee的连接池，继承ReconnectMixin，实现自动重连
class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


DB = ReconnectMySQLDatabase('shop_user', user='root', password='root', host='47.119.22.7', max_connections=8)