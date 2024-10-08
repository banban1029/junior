from flask import Flask, request
import json
import os
import inspect
import random
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# 予約可能なスロットの生成
start_date = datetime(2022, 3, 1)
end_date = datetime(2022, 4, 30)
available_slots = []

# 日付を生成し、各日付にAMとPMを追加 "YYYY/MM/DD", "AM"
current_date = start_date
while current_date <= end_date:
    available_slots.append((current_date.strftime("%Y/%m/%d"), "AM"))
    available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))
    current_date += timedelta(days=1)
    
# ランダムに50%のスロットを予約済みとして設定
number_of_booked_slots = len(available_slots) // 2
booked_slots = random.sample(available_slots, number_of_booked_slots)

# 予約済みスロットの表示
print("予約済みスロット:", booked_slots)

@app.route('/', methods=['POST'])
def index():
    # DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
    input = request.json["queryResult"]["parameters"]["any"]
    printV('Received: ' + input)

    # 日時の希望を正規表現で取得 "2022/03/01 午前"
    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})\s*(午前|午後)', input)
    
    if match:
        desired_date = match.group(1)  # "YYYY/MM/DD"
        desired_time = match.group(2)  # "AM" or "PM"

        # 予約可能かどうかを確認
        if (desired_date, desired_time) in booked_slots:
            message = f"{desired_date}の{desired_time}は予約が埋まっています。"
        else:
            message = f"{desired_date}の{desired_time}は予約可能です。"
    else:
        message = "正しい日付と時間を指定してください。"

    # Dialogflow(Firebase)へのWebhookレスポンス作成
    response = makeResponse(message, continueFlag=False)  # 会話は1ターンのみのやりとりなのでFalse
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
