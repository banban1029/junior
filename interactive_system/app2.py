from flask import Flask, request
import json
import os
import inspect

# Flaskの初期化
app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    # DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
    # Google Assistantが音声入力をキャッチしたメッセージを取得し、input変数に代入
    input = request.json["queryResult"]["parameters"]["any"]
    printV('Received: ' + input)
    
    # 認識可能なactivityを辞書として定義
    activities = {
        "温泉ツアー": "温泉ツアーですね",
        "遊園地ツアー": "遊園地ツアーですね",
        "バスツアー": "バスツアーですね"
    }

    # 入力されたactivityが辞書に存在するかを確認
    if input in activities:
        # 辞書に一致するactivityがあれば、対応するメッセージを返す
        message = activities[input]
    else:
        # 一致するactivityがなければ、エラーを返す
        message = "そのサービスはありません"
    
    # Dialogflow(Firebase)へのWebhookレスポンス作成
    # 会話は1ターンのみのやりとりなのでFalse
    response = makeResponse(message, continueFlag= False) 
    
    # Webhookレスポンス送信
    return json.dumps(response)

# Webhookレスポンスの作成(JSON形式)
def makeResponse(message, continueFlag=True):
    response = {
        "payload": {
            "google": {
                "expectUserResponse": continueFlag,
                "richResponse": {
                    "items": [
                        {
                            "simpleResponse": {
                                "textToSpeech": message
                            }
                        }
                    ]
                }
            }
        },
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        message
                    ]
                }
            }
        ]
    }
    return response

# 詳細情報(Verbose)付き出力
def printV(content):
    frame = inspect.currentframe().f_back
    print(content, end='')
    print(' (file: ' + os.path.basename(frame.f_code.co_filename) + ', function: ' + frame.f_code.co_name + ', line: ' + str(frame.f_lineno) + ')')
