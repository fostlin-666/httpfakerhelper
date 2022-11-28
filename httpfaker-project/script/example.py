from httpfaker.utils.faker_tool import Provider

class MyProvider(Provider):
    def verify_account(self, username, password):
        users = {
            'user001': '123456',
            'user002': '654321',
            'user003': '123456'
        }
        if username in users and users.get(username) == password:
            return {"code": 200, "msg": "请求成功"}
        elif username not in users:
            return {'code': 1002, 'msg': "用户不存在"}
        else:
            return {"code": 1001, "msg": "密码不正确"}

    def gen_token(self, username):
        return {"token": self.uuid()}
