# coding: utf-8
import _thread as thread
import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
import websocket


class Ws_Param(object):
    # 初始化
    def __init__(self, APIKey, APISecret, gpt_url):
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(parameter)
    # 发送请求参数
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    global answer
    data = json.loads(message)
    answer += data['payload']['choices']['text'][0]['content'].strip()
    # print(answer)
    # print(data['payload']['choices']['text'])
    code = data['header']['code']
    choices = data["payload"]["choices"]
    status = choices["status"]
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    if status == 2:
        print("#### 关闭会话")
        ws.close()

    # webSocket 请求的参数


parameter = {
    "payload": {
        "message": {
            "text": [
                {
                    "role": "system",
                    "content": "你是一位人工智能专家,目标任务,请根据我的问题，写出合适的答案， 不需要复述问题，不需要说你好，直接用两句话概括性解答。"
                },
                {
                    "role": "user",
                    "content": "你好啊"
                }
            ]
        }
    },
    "parameter": {
        "chat": {
            "max_tokens": 400,
            "domain": "4.0Ultra",
            "top_k": 4,
            "temperature": 0.5
            # "max_tokens": 4000,
            # "domain": "lite",
            # "top_k": 4,
            # "temperature": 0.5
        }
    },
    "header": {
        "app_id": "f53f75ee"
    }
}
parameter["parameter"]["chat"]["show_ref_label"] = True

def give_question(question):
    # parameter['payload']['message']['text'][1]['content'] =  question
    parameter['payload']['message']['text'][1]['content'] = question

def main(api_secret, api_key, gpt_url):
    global answer
    answer = ''  # 每次调用 main 时清空 answer
    wsParam = Ws_Param(api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return answer


def get_answer(question):

    give_question(question)

    answer = main(
        api_secret='ODE2YjE1YWM0NzYyNjRiNjY1ZmQ3Mjhi',
        api_key='958942f5cb6e4208fedbe1b1f1cadec7',
        gpt_url='wss://spark-api.xf-yun.com/v4.0/chat',  # 例如 wss://spark-api.xf-yun.com/v4.0/chat
        # api_secret='ODE2YjE1YWM0NzYyNjRiNjY1ZmQ3Mjhi',
        # api_key='958942f5cb6e4208fedbe1b1f1cadec7',
        # gpt_url='wss://spark-api.xf-yun.com/v1.1/chat',  # 例如 wss://spark-api.xf-yun.com/v4.0/chat

    )

    return answer


# if __name__ == "__main__":
#
#     give_question('1+1等于几')
#
#     answer =main(
#         api_secret='ODE2YjE1YWM0NzYyNjRiNjY1ZmQ3Mjhi',
#         api_key='958942f5cb6e4208fedbe1b1f1cadec7',
#         gpt_url='wss://spark-api.xf-yun.com/v4.0/chat',  # 例如 wss://spark-api.xf-yun.com/v4.0/chat
#     )
#
#     print(answer)
