import time
from datetime import date
import grpc
from passlib.hash import pbkdf2_sha256
from user.proto import user_pb2_grpc, user_pb2
from user.model.models import User
from loguru import logger
from peewee import DoesNotExist
from google.protobuf import empty_pb2


def convert_user(user):
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

    return user_info_rsp


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
            user_info_rsp = convert_user(user)
            rsp.data.append(user_info_rsp)
        return rsp

    @logger.catch()
    def GetUserById(self, request, context):
        try:
            user = User.get(User.id == request.id)
            user_info_rsp = convert_user(user)
            return user_info_rsp
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('user not found')
            return user_pb2.UserInfoResponse()

    @logger.catch()
    def GetUserByMobile(self, request, context):
        try:
            user = User.get(User.mobile == request.mobile)
            user_info_rsp = convert_user(user)
            return user_info_rsp
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('user not found')
            return user_pb2.UserInfoResponse()

    @logger.catch()
    def CreateUser(self, request, context):
        try:
            User.get(User.mobile == request.mobile)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('user exist')
            return user_pb2.UserInfoResponse()
        except DoesNotExist as e:
            pass
        user = User()
        user.nick_name = request.nickname
        user.mobile = request.mobile
        user.password = pbkdf2_sha256.hash(request.password)
        user.save()

        return convert_user(user)

    @logger.catch()
    def UpdateUser(self, request, context):
        try:
            user = User.get(User.id == request.id)
            user.nick_name = request.nickname
            user.gender = request.gender
            user.birthday = date.fromtimestamp(request.birthday)
            user.save()
            return empty_pb2.Empty()
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('user not found')
            return user_pb2.UserInfoResponse()

    @logger.catch()
    def CheckPassword(self, request, context):
        return user_pb2.CheckResponse(result=pbkdf2_sha256.verify(request.password, request.encryptedPassword))