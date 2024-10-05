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
# 予約可能スロットの生成関数（ルールに基づく）
def generate_slots_with_rules(start_date, end_date, activity):
    available_slots = []
    current_date = start_date

    # ルールの適用
    while current_date <= end_date:
        # 温泉ツアー: 4月は予約不可
        if activity == "温泉ツアー":
            if current_date.month == 4:
                current_date += timedelta(days=1)
                continue
            else:
                available_slots.append((current_date.strftime("%Y/%m/%d"), "AM"))
                available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))

        # 遊園地ツアー: 3月15日〜3月31日まで予約不可
        if activity == "遊園地ツアー":
            if current_date.month == 3 and 15 <= current_date.day <= 31:
                current_date += timedelta(days=1)
                continue
            else:
                available_slots.append((current_date.strftime("%Y/%m/%d"), "AM"))
                available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))

        # バスツアー: 平日は午前中が予約不可
        if activity == "バスツアー":
            if current_date.weekday() < 5:  # 平日
                available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))  # 午後のみ
            else:
                available_slots.append((current_date.strftime("%Y/%m/%d"), "AM"))
                available_slots.append((current_date.strftime("%Y/%m/%d"), "PM"))

        current_date += timedelta(days=1)

    return available_slots

# 予約済みのスロットを固定で生成
def generate_booked_slots(available_slots, rate):
    booked_count = int(len(available_slots) * rate)
    booked_slots = random.sample(available_slots, booked_count)  # ランダムな予約済みスロットを選択
    return booked_slots

# 予約スロット生成（ルール適用）および予約状況の管理
available_slots_per_location = {}
booked_slots_per_location = {}

for activity, locations in activity_data.items():
    for location in locations:
        # スロットを生成
        available_slots = generate_slots_with_rules(start_date, end_date, activity)
        
        # activityごとの予約可能スロットの生成
        available_slots_per_location[location] = available_slots
        
        # 予約済みスロットの割合を設定
        if activity == "温泉ツアー":
            # 土曜日の午後だけに混雑割合0.8を適用
            saturday_pm_slots = [slot for slot in available_slots if datetime.strptime(slot[0], "%Y/%m/%d").weekday() == 5 and slot[1] == "PM"]

            # 土曜日午後以外は通常の割合0.5を適用
            other_slots = [slot for slot in available_slots if not (datetime.strptime(slot[0], "%Y/%m/%d").weekday() == 5 and slot[1] == "PM")]

            booked_saturday_pm_slots = generate_booked_slots(saturday_pm_slots, 0.6)
            booked_other_slots = generate_booked_slots(other_slots, 0.4)

            # 土曜日午後とその他のスロットを結合
            booked_slots_per_location[location] = booked_saturday_pm_slots + booked_other_slots
            
        elif activity == "遊園地ツアー":
            if location in ["USJ", "ディズニーランド", "ディズニーシー"]:  # 混雑しやすい遊園地
                weekday_slots = [slot for slot in available_slots if datetime.strptime(slot[0], "%Y/%m/%d").weekday() < 5]  # 平日スロット
                weekend_slots = [slot for slot in available_slots if datetime.strptime(slot[0], "%Y/%m/%d").weekday() >= 5]  # 週末スロット
                booked_weekday_slots = generate_booked_slots(weekday_slots, 0.6) # 平日60%予約済み
                booked_weekend_slots = generate_booked_slots(weekend_slots, 0.8) # 週末は80%予約済み
                booked_slots_per_location[location] = booked_weekday_slots + booked_weekend_slots
            else:
                weekday_slots = [slot for slot in available_slots if datetime.strptime(slot[0], "%Y/%m/%d").weekday() < 5]  # 平日スロット
                weekend_slots = [slot for slot in available_slots if datetime.strptime(slot[0], "%Y/%m/%d").weekday() >= 5]  # 週末スロット
                booked_weekday_slots = generate_booked_slots(weekday_slots, 0.4) # 平日30%予約済み
                booked_weekend_slots = generate_booked_slots(weekend_slots, 0.5) # 週末は40%予約済み
                booked_slots_per_location[location] = booked_weekday_slots + booked_weekend_slots
        
        elif activity == "バスツアー":
            booked_slots_per_location[location] = generate_booked_slots(available_slots, 0.2)


# ユーティリティ関数を追加
def read_file(filepath, type, initial_value=None):
    if glob.glob(filepath):  # .txtが見つかった場合
        printV(filepath + ' is found!')
        with open(filepath, mode='r', encoding='utf-8') as r:
            if type == 'int':
                return int(r.read().strip())
            else:
                return r.read().strip()
    else:  # .txtが見つからなかった場合
        printV(filepath + ' is not found!')
        with open(filepath, mode='w', encoding='utf-8') as w:
            w.write(str(initial_value)) # 初期化
            return initial_value

def write_file(filepath, content): 
    if glob.glob(filepath):  # .txtが見つかった場合
        printV(filepath + ' is found!')
        with open(filepath, mode='w', encoding='utf-8') as w:
            w.write(str(content))
            return content
    else:  # .txtが見つからなかった場合
        printV(filepath + ' is not found!')
        printV('Error:')


  
        
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
        continueFlag = True
        
        # 状態(state)の取得
        data_path = os.getcwd() + '/state.txt'
        data_path0 = os.getcwd() + '/scheduled.txt'
        data_path1 = os.getcwd() + '/activity.txt'
        data_path2 = os.getcwd() + '/location.txt'
        data_path3 = os.getcwd() + '/date.txt'
        data_path4 = os.getcwd() + '/attempt_count.txt'
        
        # index関数内のファイル読み書きのリファクタリング
        state = read_file(data_path, 'int', 1)
        user_data["activity"] = read_file(data_path1, 'str', None)
        user_data["location"] = read_file(data_path2, 'str', None)
        user_data["date"] = read_file(data_path3, 'str', None)
        attempt_count = read_file(data_path4, 'int', 0)
        
        ###########################################################
        
        # 状態ファイルの確認
        # schedule.txtがHerokuサーバ上にあるかチェック
        # 予約スロットリストをアクティビティごとに schedule.txt に書き込む
        with open(data_path0, mode='w', encoding='utf-8') as f:
            for activity, locations in activity_data.items():
                    f.write(f"アクティビティ: {activity}\n")
                    f.write("=" * 40 + "\n")  # アクティビティの区切り線を追加
                    for location in locations:
                        f.write(f"場所: {location}\n")
                        f.write("-" * 30 + "\n")  # 場所の区切り線を追加
                        # 予約済みスロットの出力
                        f.write("予約済みスロット:\n")
                        booked_slots = booked_slots_per_location.get(location, [])
                        if booked_slots:
                            for slot in booked_slots:
                                date, time = slot
                                f.write(f"  日付: {date}, 時間帯: {time}\n")  # 見やすい形式で出力
                        else:
                            f.write("  予約済みスロットはありません。\n")
                        f.write("\n")
                        # 予約可能スロットの出力
                        f.write("予約可能スロット:\n")
                        available_slots = available_slots_per_location.get(location, [])
                        if available_slots:
                            for slot in available_slots:
                                date, time = slot
                                if slot not in booked_slots:  # 予約済みでないスロットのみ表示
                                    f.write(f"  日付: {date}, 時間帯: {time}\n")
                        else:
                            f.write("  予約可能なスロットはありません。\n")
                        f.write("\n" + "=" * 30 + "\n\n")  # 場所ごとの区切り線を追加    
                                        
        with open(data_path0, mode='r', encoding='utf-8') as f:
            content = f.read()  # ファイルの内容を読み取る
            printV(content)  # ファイルの内容を出力 
            
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
                state = 2
            elif state == 2:
                user_data["activity"] = input
                if user_data["activity"] not in activity_data:
                    message = '申し訳ありません、そのアクティビティは選べません。温泉ツアー、遊園地ツアー、バスツアーから選んでください。'
                    state = 2
                else:                    
                    write_file(data_path1, input)
                    user_data["activity"] = read_file(data_path1, 'str', None)                    
                        
                    message = f'{user_data["activity"]}のどの場所をご希望ですか？'
                    printV(user_data["activity"])
                    state = 3
                    
            elif state == 3:
                user_data["location"] = input
                if user_data["location"] not in activity_data[user_data["activity"]]:
                    message = '申し訳ありません、その場所は選べません。リストにある場所から選んでください。'
                    state = 3
                else:                    
                    write_file(data_path2, input)
                    user_data["location"] = read_file(data_path2, 'str', None)
                        
                    message = 'ご希望の日付を教えてください。（例: 2024/10/05 AM）'
                    state = 4
            elif state == 4:
                write_file(data_path3, input)
                user_data["date"] = read_file(data_path3, 'str', None)
                        
                message = f'予約内容：{user_data["activity"]} - {user_data["location"]} - {user_data["date"]}\n'
                budget = budget_data.get(user_data["location"], 0)
                message += f'予算は{budget // 10000}万円です。予約可能か確認します...'

                # 予約可能性のチェックを入れる
                # 日付と時間の解析 
                match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})\s*(AM|PM)', user_data["date"])
                if match:
                    desired_date = match.group(1)
                    desired_time = match.group(2)
                
                    if (desired_date, desired_time) in booked_slots_per_location[user_data["location"]]:
                        message = f'{desired_date}の{desired_time}は予約が埋まっています。'
                    else:
                        message = f'{desired_date}の{desired_time}は予約可能です。'
                        budget = budget_data.get(user_data['location'], 0)
                        message += f'予算は{budget // 10000}万円です。'
                else:
                    message = '正しい日付と時間を指定してください。'
                
                attempt_count += 1
                                    
                # 予約不可の場合( 10回以上のリトライ ) 
                if attempt_count >= max_attempts:
                    message = '申し訳ありません、予約できませんでした。対話を終了します。'
                    continueFlag = False

            # 状態の更新
            write_file(data_path, int(state))
            write_file(data_path4, attempt_count)
            
    # Webhookレスポンスの作成
    response = makeResponse(message, continueFlag)
    return json.dumps(response)


# Webhookレスポンスの作成(JSON形式)
# message: Google Homeの発話内容, continueFljuag: 会話を続けるかどうかのフラグ (続ける: Yes, 終了: No)
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
    print('\n\n')
    print(content, end='')
    print(' (file: ' + os.path.basename(frame.f_code.co_filename) + ', function: ' + frame.f_code.co_name + ', line: ' + str(frame.f_lineno) + ')')


