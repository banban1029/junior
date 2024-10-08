from flask import Flask, request
import json
import os
import glob
import inspect


app = Flask(__name__)

@app.route('/', methods=['POST'])
# DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
def index():
    # Google Assistantが音声入力をキャッチしたメッセージを取得し、input変数に代入
    input = request.json["queryResult"]["parameters"]["any"]
    printV('Received: ' + input)

    if input == 'バイバイ':  # 会話を終了するメッセージ「バイバイ」を受け取った場合
        message = 'さようなら'
        continueFlag = False
    else:  # 通常のメッセージを受け取った場合
        message = ''
        # 状態(state)の取得
        data_path = os.getcwd() + '/state.txt'
        # state.txtがHerokuサーバ上にあるかチェック
        if glob.glob(data_path):  # state.txtが見つかった場合
            printV(data_path + ' is found!')
            with open(data_path, mode='r', encoding='utf-8') as r:  # state.txtを読み込み
                
                # state.txtから状態を取得
                state = int(r.read())
        else:  # state.txtが見つからなかった場合
            printV(data_path + ' is not found!')
            with open(data_path, mode='w', encoding='utf-8') as w:  # state.txtを作成
                w.write('1')
            state = 1

        if input == 'リセット':  # 状態をリセットする場合
            with open(data_path, mode='w', encoding='utf-8') as w:
                # state.txtに[1]を上書き
                w.write('1')
                message = '状態をリセットしました'
                continueFlag = False
        else:  
            # 状態に応じて異なる発話を生成
            if state == 1:
                message = '初めまして！'
            elif state == 2:
                message ='また話しかけてくれたんですね！'
            else:
                message = '流石にもうウザイですよ...'
            continueFlag = True
            
            # 状態の更新
            with open(data_path, mode='w', encoding='utf-8') as w:
                w.write(str(state + 1))

        printV('state is ' + str(state))

    # Dialogflow(Firebase)へのWebhookレスポンス作成
    response = makeResponse(message, continueFlag)
    # Webhookレスポンス送信
    return json.dumps(response)

# Webhookレスポンスの作成(JSON形式)
# message: Google Homeの発話内容, continueFlag: 会話を続けるかどうかのフラグ (続ける: Yes, 終了: No)
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

