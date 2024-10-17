from flask import Flask, request
import json
import os
import glob
import inspect
import random
from datetime import datetime, timedelta
import re

# Flaskの初期化
app = Flask(__name__)

# activity_dataの読み込み
activity_data = {
    "温泉ツアー": ["登別", "有馬", "別府", "草津", "白浜"],
    "遊園地ツアー": ["USJ", "ディズニーランド", "ディズニーシー", "花やしき", "ひらかたパーク"],
    "バスツアー": ["中華街", "黒潮市場", "姫路城"]
}

# ツアー名と場所の組み合わせで予算を管理
budget_data = {
    ("温泉ツアー", "登別"): 130000, ("温泉ツアー", "有馬"): 50000, ("温泉ツアー", "別府"): 100000,
    ("温泉ツアー", "草津"): 70000, ("温泉ツアー", "白浜"): 50000,
    ("遊園地ツアー", "USJ"): 30000, ("遊園地ツアー", "ディズニーランド"): 50000, 
    ("遊園地ツアー", "ディズニーシー"): 50000, ("遊園地ツアー", "花やしき"): 40000, 
    ("遊園地ツアー", "ひらかたパーク"): 10000,
    ("バスツアー", "中華街"): 15500, ("バスツアー", "黒潮市場"): 15500, 
    ("バスツアー", "姫路城"): 10000, ("バスツアー", "ディズニーランド"): 40000, 
    ("バスツアー", "有馬"): 10000
}

# user_dataの初期化
user_data = {
    "activity": None,
    "location": None,
    "date": None
}

# 予約可能性のチェックのためのカウンタ, 10回超えたら予約不可
max_attempts = 10

# 予約可能なスロットの生成
start_date = datetime(2022, 3, 1)
end_date = datetime(2022, 4, 30)

# 稼働日の取得
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

# 予約可能スロットの生成
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

# スロットをファイルに保存する関数
def save_slots_to_file(file_name, booked_slots_per_location):
    with open(file_name, 'w') as f:
        json.dump(booked_slots_per_location, f, ensure_ascii=False, indent=4)


# スロットをファイルから読み込む関数
def load_slots_from_file(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

# 予約スケジュールの可視化関数
def print_booked_slots(booked_slots_per_location, available_slots_per_location, activity_data):
    for activity, locations in activity_data.items():
        print(f"アクティビティ: {activity}")
        print("=" * 40)
        for location in locations:
            print(f"場所: {location}")
            print("-" * 30) # アクティビティの区切り線を追加
            # 予約済みスロットの出力
            print("予約済みスロット:")
            booked_slots = booked_slots_per_location.get(location, [])
            if booked_slots:
                for slot in booked_slots:
                    date, time = slot
                    print(f"  日付: {date}, 時間帯: {time}")
            else:
                print("  予約済みスロットはありません。")
            # 予約可能スロットの出力
            print("\n予約可能スロット:")
            available_slots = available_slots_per_location.get(location, [])
            if available_slots:
                for slot in available_slots:
                    date, time = slot
                    if slot not in booked_slots:
                        print(f"  日付: {date}, 時間帯: {time}")
            else:
                print("  予約可能なスロットはありません。")
            print("\n" + "=" * 30 + "\n")


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
    # DialogflowからWebhookリクエストが来るとindex()関数が呼び出される
    # Google Assistantが音声入力をキャッチしたメッセージを取得し、input変数に代入    
    input = request.json["queryResult"]["parameters"]["any"]
    printV('Received: ' + input)
    
    ######################################################################################
    # メッセージの初期化
    message = ''
    continueFlag = True
    
    # dataパスの取得
    data_path = os.getcwd() + '/state.txt' # 状態を保存用
    data_path1 = os.getcwd() + '/activity.txt' # アクティビティを保存用
    data_path2 = os.getcwd() + '/location.txt' # 場所を保存用
    data_path3 = os.getcwd() + '/itinerary.txt' # 日時を保存用
    data_path4 = os.getcwd() + '/attempt_count.txt' # 予約可能性のチェックのためのカウンタ
    data_path5 = os.getcwd() + '/available_slots.txt' # 予算を保存用
    
    # data所得
    state = read_file(data_path, 'int', 1)
    user_data["activity"] = read_file(data_path1, 'str', None)
    user_data["location"] = read_file(data_path2, 'str', None)
    user_data["date"] = read_file(data_path3, 'str', None)
    attempt_count = read_file(data_path4, 'int', 0)
    
    # 予約始まってから、固定させる。
    if(state == 1):
        global booked_slots_per_location
        save_slots_to_file(data_path5, booked_slots_per_location)

    # スロットを読み込む
    booked_slots_per_location = {}
    booked_slots_per_location = load_slots_from_file(data_path5)
    # 読み込んだデータを確認
    print_booked_slots(booked_slots_per_location, available_slots_per_location, activity_data)

    ######################################################################################  
    
    if input == 'バイバイ':  # 会話を終了するメッセージ「バイバイ」を受け取った場合
        message = 'さようなら'
        continueFlag = False
    else:  # 通常のメッセージを受け取った場合
       
        ###########################################################
        if input == 'リセット':  # 状態をリセットする場合
            state = 1
            message = '状態をリセットしました'
            continueFlag = False
        ###########################################################
        else:             
            # 状態に応じて異なる発話を生成
            if state == 1:
                message = 'どのアクティビティをご希望ですか？'
                state = 2
                
            # activityの選択
            elif state == 2:
                user_data["activity"] = input
                if user_data["activity"] not in activity_data:
                    message = '申し訳ありません、そのアクティビティは選べません。温泉ツアー、遊園地ツアー、バスツアーから選んでください。'
                    state = 2
                else:                      
                    write_file(data_path1, user_data["activity"])  # アクティビティをファイルに書き込む                 
                    message = f'{user_data["activity"]}のどの場所をご希望ですか？'
                    state = 3  
                    
            # locationの選択    
            elif state == 3:
                user_data["location"] = input
                if user_data["location"] not in activity_data[user_data["activity"]]:
                    message = '申し訳ありません、その場所は選べません。リストにある場所から選んでください。'
                    state = 3
                else:                    
                    write_file(data_path2, user_data["location"])  
                    message = 'ご希望の日付を教えてください。（例: 2022/03/10 AM）'
                    state = 4
                    
            # dateの選択
            elif state == 4:
                user_data["date"] = input
                write_file(data_path3, user_data["date"])
                message = f'予約内容：{user_data["activity"]} - {user_data["location"]} - {user_data["date"]}\n'
                budget = budget_data.get((user_data["activity"], user_data["location"]), 0)
                message += f'予算は{budget // 10000}万円です。こちらでよろしいですか？ (はい/いいえ)'
                state = 5
                
            # 予約の確認
            elif state == 5:
                if input == 'はい':
                    # 予約可能性のチェックを入れる
                    # 日付と時間の解析 
                    # user_data["date"] = "2022/03/01 AM"
                    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})\s*(AM|PM)', user_data["date"])
                    desired_date = match.group(1)
                    desired_time = match.group(2)
                    date_time  = []
                    date_time.append([desired_date, desired_time])
                    
                    if match:
                        year, month, day = map(int, desired_date.split('/'))
                        desired_date = datetime(year=int(year), month=int(month), day=int(day))
                        
                        if desired_date < start_date or desired_date > end_date:
                            message = 'その日付は予約できません。もう一度入力してください'
                            state = 4
                        elif all(item in booked_slots_per_location[user_data["location"]] for item in date_time):
                            message = f'{user_data["date"]}は予約が埋まっています。'
                            state = 4
                            attempt_count += 1
                        else:
                            message = f'{user_data["date"]}は予約が完了です。' 
                            budget = budget_data.get((user_data["activity"], user_data["location"]), 0)
                            message += f'予算は{budget // 10000}万円です。'
                    else:
                        message = "正しい日付時間形式で入力してください。例: 2022/03/01 AM"
                        state = 4
                                            
                    # 予約不可の場合( 10回以上のリトライ ) 
                    if attempt_count >= max_attempts:
                        message = '申し訳ありません、予約できませんでした。対話を終了します。'
                        continueFlag = False
                        state = 1
                        
                elif input == "いいえ":
                    message = '予約希望を取り消しました。もう一度入力してください'
                    state = 1

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
