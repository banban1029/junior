from flask import Flask, request
import json
import os
import inspect

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    # DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
    # Google Assistantが音声入力をキャッチしたメッセージを取得し、input変数に代入
    input = request.json["queryResult"]["parameters"]["any"]
    printV('Received: ' + input)
    
    # 認識可能なアクティビティを辞書として定義
    activities = {
        "温泉ツアー": "温泉ツアーですね",
        "遊園地ツアー": "遊園地ツアーですね",
        "バスツアー": "バスツアーですね"
    }

    # 入力されたアクティビティが辞書に存在するかを確認
    if input in activities:
        # 辞書に一致するアクティビティがあれば、対応するメッセージを返す
        message = activities[input]
    else:
        # 一致するアクティビティがなければ、エラーメッセージを返す
        message = "そのサービスはありません"
    
    # Dialogflow(Firebase)へのWebhookレスポンス作成
    response = makeResponse(message, continueFlag= False) # 会話は1ターンのみのやりとりなのでFalse
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
