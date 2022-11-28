from httpfaker.utils.faker_tool import Provider
import os
from flask import send_from_directory
from flask import Response


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

    def save_file(self, files):
        r = {
            "code": 200,
            "msg": 'upload success',
            "respData": None
        }
        try:
            file_name = files.filename
            files.save(file_name)
            r['respData'] = file_name
        except Exception as e:
            r.update({"code": 1001, 'msg': "upload faild!!! {}".format(e)})
        return r

    def download(self, file_name):
        crt_path = os.path.abspath('.')
        if not os.path.exists(file_name):
            return Response(
                response={
                    "code": 1002,
                    "msg": 'file not found!'
                }, status=200, headers={"Content-Type": "application/json"}
            )
        return send_from_directory(crt_path, filename=file_name, as_attachment=True)
