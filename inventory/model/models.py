from datetime import datetime

from peewee import CharField, ForeignKeyField, IntegerField, BooleanField, Model, DateTimeField, AutoField, FloatField, \
    DoesNotExist
from playhouse.mysql_ext import JSONField
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


DB = ReconnectMySQLDatabase('shop_inventory', user='root', password='hyxiao', host='127.0.0.1', max_connections=8)


class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now, verbose_name='创建时间')
    update_time = DateTimeField(default=datetime.now, verbose_name='更新时间')
    is_deleted = BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        database = DB

    def save(self, *args, **kwargs):
        if self._pk is not None:
            self.update_time = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def delete(cls, permanently=False):
        if permanently:
            return super().delete()
        else:
            return super().update(is_deleted=True)

    def delete_instance(self, permanently=False, recursive=False, delete_nullable=False):
        if permanently:
            return self.delete(permanently).where(self._pk_expr()).execute()
        else:
            self.is_deleted = True
            self.save()

    @classmethod
    def select(cls, *fields):
        return super().select(*fields).where(cls.is_deleted == False)


class Inventory(BaseModel):
    # 商品的库存表
    # stock = PrimaryKeyField(Stock)
    goods = IntegerField(verbose_name="商品id", unique=True)
    stocks = IntegerField(verbose_name="库存数量", default=0)
    version = IntegerField(verbose_name="版本号", default=0)  # 分布式锁的乐观锁

class InventoryNew(BaseModel):
    #商品的库存表
    # stock = PrimaryKeyField(Stock)
    goods = IntegerField(verbose_name="商品id", unique=True)
    stocks = IntegerField(verbose_name="库存数量", default=0)
    version = IntegerField(verbose_name="版本号", default=0) #分布式锁的乐观锁
    freeze = IntegerField(verbose_name="冻结数量", default=0)

class InventoryHistory(BaseModel):
    # 出库历史表
    order_sn = CharField(verbose_name="订单编号", max_length=20, unique=True)
    order_inv_detail = CharField(verbose_name="订单详情", max_length=200)
    status = IntegerField(choices=((1, "已扣减"), (2, "已归还")), default=1, verbose_name="出库状态")


if __name__ == "__main__":
    DB.create_tables([Inventory])

    for i in range(421, 841):
        try:
            inv = Inventory.get(Inventory.goods == i)
            inv.stocks = 100
            inv.save()
        except DoesNotExist as e:
            inv = Inventory(goods=i, stocks=100)
            inv.save()

