# http-faker

#### 介绍
**灵活又简单的mock服务**

gitee地址： https://gitee.com/guojongg/http-faker

httpfaker基于faker和flask库，提供强大的逻辑处理能力；通过对配置文件（yaml/json）的描述，可返回想要的任意数据。

httpfaker针对返回数据的规则编写灵活，简单。除了可以满足传统的接口mock外，还支持处理业务逻辑，可实现真正的业务功能。

适用于：
* 前端人员： 前后端分离开发，无需等到后台接口实现即可开始进行页面请求
* 测试人员： 提前进行接口测试代码编写；**服务未至，用例先行**
* 其他需要写一个简单api的人员： 通过yaml文件配置，可减少开发代码；无需关注请求处理部分，只需关注自己的业务逻辑即可。

#### 软件架构
本工具可通过编写yaml/json文件来描述接口数据返回，除了传统的mock数据外，还支持自定义的逻辑处理。比如实现一个真正的用户登录：

>通过yaml文件描述用户登录时的处理逻辑: 接收到前端请求的用户名和密码之后，在数据库中验证账号是否存在，
存在的话在redis中存入用户token并返回用户token。这个流程需要用到两个方法，一是数据库验证，二是redis token创建，这两个逻辑通过自定义方法实现，
其他配置通过yaml文件描述即可。具体可参考示例。


#### 安装教程

```
# 源码安装
git clone https://gitee.com/guojongg/http-faker.git
cd http-faker
python setup.py install

# pip安装
pip install httpfaker
```

#### 使用说明

##### 一、生成模板
可使用http2api可直接生成模板，后续完善模板中的返回数据配置即可。

**http2api使用说明**

通过`http2api`命令启动`http2api`服务，使用前端浏览器或postman等接口调用工具调用相关需要mock的接口。
调用成功后将在指定目录生成接口描述文件。后续编辑此文件，完善response部分内容即可。
```shell script
(venv) guolong@guolong-PC:~/01Work/07MyProject/http-faker$ http2api -h
usage: http2api [-h] [--default-body [DEFAULT_BODY]]
                [--default-status [DEFAULT_STATUS]] [--path [PATH]]
                [--hide-data] [--out-format [OUT_FORMAT]] [--listen [LISTEN]]
                [--port [PORT]]

调用接口生成mock描述文件

optional arguments:
  -h, --help            show this help message and exit
  --default-body [DEFAULT_BODY]
                        Response默认的返回体，指定后生成的Response中的body字段将按照此定义来生成。用法：指定文件
                        路径，文件内容格式可以是json或者yaml！
  --default-status [DEFAULT_STATUS]
                        Response中status_code返回值，默认为200
  --path [PATH]         输出的配置文件存放路径, 默认当前目录下的apis目录
  --hide-data           不转换Request中的请求体和请求参数数据（请求参数和请求体数据仅做参考，不参与实际逻辑）
  --out-format [OUT_FORMAT]
                        转换的配置文件的格式；可选yml和json，默认yml格式
  --listen [LISTEN]     启动服务默认监听地址，默认0.0.0.0
  --port [PORT]         启动服务默认监听端口，默认9000

(venv) guolong@guolong-PC:~/01Work/07MyProject/http-faker$ http2api 
 * Serving Flask app "httpfaker.http2yml" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:9000/ (Press CTRL+C to quit)

```

##### 二、开始mock
当接口模板文件编辑好后，可使用`httpfaker`命令来启动mock服务；启动后前端访问指定的接口即可按照模板文件中描述的内容进行接口返回。

**httpfaker使用说明**
```shell script
(venv) guolong@guolong-PC:~/01Work/07MyProject/http-faker$ httpfaker -h
usage: httpfaker [-h] [--api_path [API_PATH]] [--script_path [SCRIPT_PATH]]
                 [--listen [LISTEN]] [--port [PORT]]

启动一个mock服务

optional arguments:
  -h, --help            show this help message and exit
  --api_path [API_PATH]
                        api描述文件所在路径， 默认apis
  --script_path [SCRIPT_PATH]
                        自定义方法脚本所在目录, 默认script
  --listen [LISTEN]     启动服务默认监听地址，默认0.0.0.0
  --port [PORT]         启动服务默认监听端口，默认9001


(venv) guolong@guolong-PC:~/01Work/07MyProject/http-faker$ httpfaker 
 * Serving Flask app "httpfaker.utils.http_mock" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:9001/ (Press CTRL+C to quit)
```
##### 三、api格式说明
api描述文件由`import`、`env`、`request`、`logic`、`response`几部分组成：
* `import`: &nbsp;&nbsp;动态导入Python的库，在jinja2模板中使用（可选）
* `env`: &nbsp;&nbsp;预定义的全局变量，可被下面的字段引用（可选）
* `request`: &nbsp;&nbsp; 请求参数的描述；httpfaker会根据request块中的path和method字段进行接口注册，
其他字段可选，程序不做处理，可作为描述逻辑时的参考。
* `logic`: &nbsp;&nbsp; 逻辑处理描述，可在此进行业务逻辑的处理；通过调用自定义方法来处理一些业务逻辑。
比如登录，可在此处理登录时的账号校验和token生成的逻辑。（可选）
* `response`: &nbsp;&nbsp; 接口返回的字段描述，可通过灵活的赋值方式对返回的字段进行定义。也可以直接定义返回值。
```yaml
import:
  - datetime  # 动态导包，可在jinja2模板中使用
env:
  code: 200  # 上面定义的字段可被下面的字段引用
  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 赋值说明(字段赋值的几种方式) >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  # 1. 使用engine参数和rule参数进行函数调用，engine参数描述函数名，rule描述函数接收的参数
  example1:
    engine: eq
    rule:
      value: application/json
  # 2. 使用engine参数进行函数调用，忽略rule参数，可以将参数直接写在engine参数中，使用()包裹；参考Python函数调用的语法。参数较少时可以使用此方式。
  example2:
      engine: eq('application/json')
  # 3. 直接赋值，键值对就好了。
  example3: application/json  # 直接赋值也可以
  # 4. 使用jinja2模板对值动态渲染；可引用上面定义过的字段
  #    引用时需从顶级字段开始，且双大括号与具体的变量之间要空格，比如{{ env.content_type }}，
  #    不可写成{{ content_type }}或{{env.content_type}}
  example4: '{{ env.code }}'  # 引用上面定义过的变量
  # 5. 使用faker库的标准方法或自定义方法（faker对象已经注册到jinja2模板中，直接调用方法即可）
  example5: '{{ faker.name() }}'
request:
  path: /api/login  # 请求地址
  method:  # 请求方法，注意这里是list，可以有多个。
    - POST  
  data: null  # 请求的原始数据，字符串格式
  json:  # 请求的json格式的数据
    username: xiaoming
    password: '123456'
  args:  # 请求地址后面的参数
    type: mobile
logic:
  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 业务逻辑处理说明 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
  # 每个处理逻辑写一个键值对，比如账号验证就写成verify，在下方调用时可直接使用logic.verify来调用返回结果，
  # 当返回结果为字典时可根据字典中的键来调用，比如logic.verify.code。 (前提是code必须存在，否则会报错)
  # 需要注意的是，request是flask中的请求对象，在下方调用request中的属性时需要按照flask中request存在的属性进行调用；比如下面的request.json.
  verify:
    engine: verify_account('{{ request.json.username }}', '{{ request.json.password }}')
  token: '{{ faker.gen_token(request.json.username) if logic.verify.code==200 else None }}'
  print: '{{ faker.print(logic.token) }}'  # 当要调试的时候可以考虑写一个print

response:
  headers: # headers中定义的字段会放到返回头中
    Content-Type: '{{ env.example1 }}'
  body:
    code: '{{ logic.verify.code }}'
    msg: '{{ logic.verify.msg }}'
    respData: '{{ logic.token }}'
  status_code: 200  # status_code定义为请求的返回值（不是返回数据中的code）
```
