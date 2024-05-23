import grpc

from user.proto import user_pb2_grpc, user_pb2


class UserTest:
    def __init__(self):
        # 连接grpc服务器
        channel = grpc.insecure_channel("127.0.0.1:50051")
        self.stub = user_pb2_grpc.UserStub(channel)

    def user_list(self):
        rsp: user_pb2.UserListResponse = self.stub.GetUserList(user_pb2.PageInfo())
        print(rsp.total)
        for user in rsp.data:
            print(user.nickname, user.mobile)

    def get_user_by_id(self, id):
        rsp: user_pb2.UserInfoResponse = self.stub.GetUserById(user_pb2.IdRequest(id=id))
        print(rsp.nickname, rsp.mobile)

    def get_user_by_mobile(self, mobile):
        rsp: user_pb2.UserInfoResponse = self.stub.GetUserByMobile(user_pb2.MobileRequest(mobile=mobile))
        print(rsp.nickname, rsp.mobile)

    def create_user(self, nickname, password, mobile):
        rsp: user_pb2.UserInfoResponse = self.stub.CreateUser(user_pb2.CreateUserInfo(nickname=nickname, password=password, mobile=mobile))
        print(rsp.nickname, rsp.mobile)


if __name__ == "__main__":
    user = UserTest()
    user.user_list()
    user.get_user_by_id(1)
    user.get_user_by_mobile("13012345678")
    user.create_user("test", "123456", "18812345678")