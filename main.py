from flask import Flask
from flask_cors import CORS

# 初始化 Flask 应用
app = Flask(__name__)
# 开启跨域支持，这样别的地方访问就不会报错啦喵
CORS(app)

@app.route('/')
def hello_world():
    # 这是我们返回给浏览器的话
    return 'Hello, world！'

if __name__ == '__main__':
    # 运行服务器，默认端口是 5000
    app.run(debug=True)
#hsadouihqojiwp
