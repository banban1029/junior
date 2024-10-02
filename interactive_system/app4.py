from flask import Flask, request
import json
import os
import glob
import inspect
import random
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# 初期化用のデータ
activity_data = {
    "温泉ツアー": ["登別", "有馬", "別府", "草津", "白浜"],
    "遊園地ツアー": ["USJ", "ディズニーランド", "ディズニーシー", "花やしき", "ひらかたパーク"],
    "バスツアー": ["中華街", "黒潮市場", "姫路城"]
}
budget_data = {
    "登別": 130000, "有馬": 50000, "別府": 100000, "草津": 70000, "白浜": 50000,
    "USJ": 30000, "ディズニーランド": 50000, "ディズニーシー": 50000, "花やしき": 40000, "ひらかたパーク": 10000,
    "中華街": 15500, "黒潮市場": 15500, "姫路城": 10000
}

# ユーザがどの項目を入力したかを追跡するための変数を初期化
user_data = {
    "activity": None,
    "location": None,
    "date": None
}

# 予約可能性のチェックのためのカウンタ, 10回超えたら予約不可
max_attempts = 10
attempt_count = 0

# 予約可能なスロットの生成
start_date = datetime(2022, 3, 1)
end_date = datetime(2022, 4, 30)

# 予約可能なスロットの生成関数
def generate_slots(start_date, end_date):
    available_slots = []
    # 日付を生成し、各日付にAMとPMを追加
    current_date = start_date
    while current_date <= end_date:
        available_slots.append((current_date.strftime("%Y/%m/%d"), "AM"))
        available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))
        current_date += timedelta(days=1)
    return available_slots

# 各アクティビティと場所ごとに予約可能スロットを管理
available_slots_per_location = {}
for activity, locations in activity_data.items():
    for location in locations:
        available_slots_per_location[location] = generate_slots(start_date, end_date)

# ランダムに50%のスロットを予約済みとして設定
booked_slots_per_location = {}
for location, slots in available_slots_per_location.items():
    number_of_booked_slots = len(slots) // 2
    booked_slots_per_location[location] = random.sample(slots, number_of_booked_slots)

@app.route('/', methods=['POST'])
# DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
def index():
    global attempt_count
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
        
        # 状態ファイルの確認
        # state.txtがHerokuサーバ上にあるかチェック
        if glob.glob(data_path):  # state.txtが見つかった場合
            printV(data_path + ' is found!')
            with open(data_path, mode='r', encoding='utf-8') as r:
                
                # state.txtから状態を取得
                state = int(r.read())
        else:  # state.txtが見つからなかった場合
            printV(data_path + ' is not found!')
            with open(data_path, mode='w', encoding='utf-8') as w:
                w.write('1')
            state = 1
            
        ###########################################################
        
        if input == 'リセット':  # 状態をリセットする場合
            with open(data_path, mode='w', encoding='utf-8') as w:
                # state.txtに[1]を上書き
                w.write('1')
                message = '状態をリセットしました'
                continueFlag = False
        else: 
            # 状態に応じて異なる発話を生成
            if state == 1:
                message = 'どのアクティビティをご希望ですか？（温泉ツアー、遊園地ツアー、バスツアーから選んでください）'
                user_data['activity'] = input
                state += 1
            elif state == 2:
                if user_data['activity'] not in activity_data:
                    message = '申し訳ありません、そのアクティビティは選べません。温泉ツアー、遊園地ツアー、バスツアーから選んでください。'
                else:
                    message = f'{user_data["activity"]}のどの場所をご希望ですか？'
                    user_data['location'] = input
                    state += 1
            elif state == 3:
                if user_data['location'] not in activity_data[user_data['activity']]:
                    message = '申し訳ありません、その場所は選べません。リストにある場所から選んでください。'
                else:
                    message = 'ご希望の日付を教えてください。（例: 2024/10/05 AM）'
                    user_data['date'] = input
                    state += 1
            elif state == 4:
                message = f'予約内容：{user_data["activity"]} - {user_data["location"]} - {user_data["date"]}\n'
                budget = budget_data.get(user_data['location'], 0)
                message += f'予算は{budget // 10000}万円です。予約可能か確認します...'

                # 予約可能性のチェックを入れる
                # 日付と時間の解析 
                match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})\s*(AM|PM)', user_data['date'])
                if match:
                    desired_date = match.group(1)
                    desired_time = match.group(2)
                
                    if (desired_date, desired_time) in booked_slots_per_location[user_data['location']]:
                        message = f'{desired_date}の{desired_time}は予約が埋まっています。'
                    else:
                        message = f'{desired_date}の{desired_time}は予約可能です。'
                        budget = budget_data.get(user_data['location'], 0)
                        message += f'予算は{budget // 10000}万円です。'
                else:
                    message = '正しい日付と時間を指定してください。'
                
                continueFlag = True
                
                # 予約不可の場合( 10回以上のリトライ ) 
                if attempt_count >= max_attempts:
                    message = '申し訳ありません、予約できませんでした。対話を終了します。'
                    continueFlag = False
                else:
                    message += '予約可能です！'

            # 状態の更新
            with open(data_path, mode='w', encoding='utf-8') as w:
                w.write(str(state))

    # カウントを増やす
    attempt_count += 1

    # Webhookレスポンスの作成
    response = makeResponse(message, continueFlag)
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


