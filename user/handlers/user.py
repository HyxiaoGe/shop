import time

from user.proto import user_pb2_grpc, user_pb2
from user.model.models import User
from loguru import logger


class UserService(user_pb2_grpc.UserServicer):
    @logger.catch()
    def GetUserList(self, request: user_pb2.PageInfo, context):
        # 获取用户的列表
        rsp = user_pb2.UserListResponse()

        users = User.select()
        rsp.total = users.count()

        start = 0
        per_page_num = 10
        if request.pageSize:
            per_page_num = request.pageSize
        if request.page:
            page = request.page
            start = (page - 1) * per_page_num

        users = users.limit(per_page_num).offset(start)

        for user in users:
            user_info_rsp = user_pb2.UserInfoResponse()
            user_info_rsp.id = user.id
            user_info_rsp.mobile = user.mobile
            user_info_rsp.password = user.password
            user_info_rsp.role = user.role

            if user.nick_name:
                user_info_rsp.nickname = user.nick_name
            if user.birthday:
                user_info_rsp.birthday = int(time.mktime(user.birthday.timetuple()))
            if user.gender:
                user_info_rsp.gender = user.gender

            rsp.data.append(user_info_rsp)
        return rsp