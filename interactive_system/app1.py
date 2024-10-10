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

    # 定型的な返答を格納する辞書
    res_map = {
        'こんにちは': 'こんにちは！お元気ですか？',
        'おはよう': 'おはようございます！今日は何をしますか？',
        'ありがとう': 'どういたしまして！',
        'おやすみ': 'おやすみ～いい夢を',
        'ごめんね': '気にしないでください！',
    }
    
    # 会話を終了するメッセージ「バイバイ」を受け取った場合
    if input == 'バイバイ':
        message = 'さようなら'
        continueFlag = False
    # ユーザの入力に応じて返答を決定
    elif input in res_map:  # 定型的な返答がある場合
        message = res_map[input]
        continueFlag = True
    else:  # 通常のメッセージを受け取った場合
        message = f'{input}と言いましたね'
        continueFlag = True

    # Dialogflow(Firebase)へのWebhookレスポンス作成
    response = makeResponse(message, continueFlag)
    # Webhookレスポンス送信
    return json.dumps(response)

# Webhookレスポンスの作成(JSON形式)
# message: Google Homeの発話内容, continueFlag: 会話を続けるかどうかのフラグ（続ける: Yes, 終了: No）
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
