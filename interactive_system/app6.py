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
    "date": None,
    "time": None
}

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
        data_path1 = os.getcwd() + '/activity.txt'
        data_path2 = os.getcwd() + '/location.txt'
        data_path3 = os.getcwd() + '/itinerary.txt'
        data_path4 = os.getcwd() + '/attempt_count.txt'
        data_path5 = os.getcwd() + '/booked_slots.txt'
        data_path6 = os.getcwd() + '/error_recovery.txt'
        
        # index関数内のファイル読み書きのリファクタリング
        state = read_file(data_path, 'int', 1)
        user_data["activity"] = read_file(data_path1, 'str', None)
        user_data["location"] = read_file(data_path2, 'str', None)
        # 日時の読み込み (YYYY/MM/DD time 形式)、 内容をトリミングして空白で分割
        user_data["date"], user_data["time"] = read_file(data_path3, 'str', "None None").strip().split()  
        attempt_count = read_file(data_path4, 'int', 0)
        error_recovery = read_file(data_path6, 'int', 0)
        budget = budget_data.get(user_data["location"], 0)
        # 予約可能性のチェックのためのカウンタ, 10回超えたら予約不可
        max_attempts = 10
        
        # 予約始まってから、固定させる。
        if(state == 1):
            global booked_slots_per_location
            save_slots_to_file(data_path5, booked_slots_per_location)
    
        # スロットを読み込む
        booked_slots_per_location = {}
        booked_slots_per_location = load_slots_from_file(data_path5)

        # 読み込んだデータを確認
        print_booked_slots(booked_slots_per_location, available_slots_per_location, activity_data)
            
        ###########################################################
        if input == 'リセット':  # 状態をリセットする場合
            state = 1
            message = '状態をリセットしました'
            continueFlag = False
                    
        elif input == '戻る':  # 状態をリセットする場合
            message = '1つ前のステップに戻ります。\n'
            state -= 1
            
            if state ==1 or state == 2:
                if state == 1:
                    state = 2
                message += 'どのアクティビティをご希望ですか？\n'
            elif state == 3:
                message += f'どの場所をご希望ですか？\n'
            elif state == 4:
                message += 'ご希望の日程はいかがなさいますか？\n'
            
        else:    
            # 状態に応じて異なる発話を生成
            if state == 1:
                message = 'どのアクティビティをご希望ですか？\n'
                state = 2
            elif state == 2:   
                # 課題5用　柔軟な入力を受け付ける(正規表現)
                # アクティビティの正規表現パターンを作成
                # ユーザーの入力にアクティビティ、場所、日時が含まれているか確認
                pattern_activity = r'(温泉|遊園地|バス)'  # アクティビティの正規表現
                pattern_location = r'|'.join([re.escape(location) for locations in activity_data.values() for location in locations])  # 場所の正規表現
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  # 日付の正規表現（例: 2023/04/02）
                pattern_time = r'(AM|PM|am|pm|午前|午後)'  # 時間帯の正規表現
                
                # 入力文を正規表現で解析
                match_activity = re.search(pattern_activity, input)  # アクティビティを検索
                match_location = re.search(pattern_location, input)  # 場所を検索
                match_date = re.search(pattern_date, input)  # 日付を検索
                match_time = re.search(pattern_time, input)  # 時間帯を検索

                if match_activity and match_location and match_date and match_time:
                        # アクティビティ、場所、日時すべてが含まれている場合
                        user_data["activity"] = match_activity.group() + "ツアー"
                        user_data["location"] = match_location.group()
                        user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"  # YYYY/MM/DD形式でフォーマット
                        user_data["time"] = match_time.group().upper() if match_time else ''  # AM/PMがあるか確認
                        budget = budget_data.get(user_data["location"], 0)

                        # ファイルに書き込む
                        write_file(data_path1, user_data["activity"])  # アクティビティをファイルに書き込む
                        write_file(data_path2, user_data["location"])  # 場所をファイルに書き込む
                        write_file(data_path3, f'{user_data["date"]} {user_data["time"]}')  # 日時をファイルに書き込む
                                   
                        # 予約内容を確認するメッセージ
                        message = (f'予約内容は、\n'
                                   f'アクティビティ: {user_data["activity"]}\n'
                                   f'場所: {user_data["location"]}\n'
                                   f'日付: {user_data["date"]} {user_data["time"]}\n'
                                   f'予算: {budget // 10000}万円\n'
                                   'でよろしいですか？ (はい/いいえ)')
                        state = 5  # 予約確認ステップへ進む
                        error_recovery = 0  # エラー回復カウンタをリセット
                        
                elif match_activity and match_location:
                        # アクティビティと場所のみ入力されている場合 -> 日時指定のステートへ進む
                        user_data["activity"] = match_activity.group() + "ツアー"
                        user_data["location"] = match_location.group()

                        write_file(data_path1, user_data["activity"])  # アクティビティをファイルに書き込む
                        write_file(data_path2, user_data["location"])  # 場所をファイルに書き込む
                        
                        message = 'ご希望の日程はいかがなさいますか。'
                        state = 4  # 日時入力ステップへ進む
                        printV(booked_slots_per_location[user_data["location"]])
                        error_recovery = 0  # エラー回復カウンタをリセット

                elif match_activity:
                    # アクティビティのみ入力された場合
                    user_data["activity"] = match_activity.group() + "ツアー"
                    write_file(data_path1, user_data["activity"])
                    
                    # 応対メッセージ
                    message = (f'{match_activity.group()}は、とても良い選択ですね！\n\n')
                    if user_data["activity"] == "温泉ツアー":
                        message += '私も週末は、温泉でリラックスしてみようと考えています...\n\n'
                    elif user_data["activity"] == "遊園地ツアー":
                        message += '乗り物優先パスもサービスでお付けしますので存分に楽しんでください！\n\n'
                    elif user_data["activity"] == "バスツアー":
                        message += 'こちらのバスツアーは、休憩時間を小まめに設けていますので、安心してご乗車いただけますよ。\n\n'

                    message += f'それでは、{user_data["activity"]}のどの場所をご希望ですか？\n'
                    state = 3  # 場所入力ステップへ進む
                    error_recovery = 0  # エラー回復カウンタをリセット
            
                else:
                    # 無効な入力があった場合
                    if(error_recovery == 0):
                        message = ( f'申し訳ありません、聞き取れませんでした。\n'
                                    f'もう一度お尋ねください。\n')                        
                    elif (error_recovery == 1):
                        message = ( f'「温泉にゆったりつかりたい！」という感じで聞いてください\n')
                    else:
                        message = ( f'「温泉ツアー」・「遊園地ツアー」・「バスツアー」の中からお選びください。\n')
                    
                    state = 2 
                    error_recovery += 1
                                
                           
            elif state == 3:
                # 課題5用　柔軟な入力を受け付ける(正規表現)
                # 場所の正規表現パターンを作成
                #'登別|有馬|別府|草津|白浜|USJ|ディズニーランド|ディズニーシー|花やしき|ひらかたパーク|中華街|黒潮市場|姫路城'                
                pattern_location = r'|'.join([re.escape(location) for locations in activity_data.values() for location in locations])  # 場所の正規表現
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  # 日付の正規表現（例: 2023/04/02）
                pattern_time = r'(AM|PM|am|pm|午前|午後)'  # 時間帯の正規表現
                
                # 入力文を正規表現で解析
                match_location = re.search(pattern_location, input)  # 場所を検索
                match_date = re.search(pattern_date, input)  # 日付を検索
                match_time = re.search(pattern_time, input)  # 時間帯を検索
                
                
                if match_location and match_date and match_time:
                    # アクティビティ、場所、日時すべてが含まれている場合       
                    user_data["location"] = match_location.group()
                    user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"  # YYYY/MM/DD形式でフォーマット
                    user_data["time"] = match_time.group().upper() if match_time else ''  # AM/PMがあるか確認
                    budget = budget_data.get(user_data["location"], 0)
                    
                    # ファイルに書き込む
                    write_file(data_path2, user_data["location"])  # 場所をファイルに書き込む
                    write_file(data_path3, f'{user_data["date"]} {user_data["time"]}')  # 日時をファイルに書き込む
                    
                    # 予約内容を確認するメッセージ
                    message = (f'予約内容は、\n'
                               f'アクティビティ: {user_data["activity"]}\n'
                               f'場所: {user_data["location"]}\n'
                               f'日付: {user_data["date"]} {user_data["time"]}\n'
                               f'予算: {budget // 10000}万円\n'
                               'でよろしいですか？ (はい/いいえ)')
                    state = 5  # 次の確認ステップへ進む
                    error_recovery = 0  # エラー回復カウンタをリセット
                elif match_location:
                    # アクティビティと場所のみ入力されている場合 -> 日時指定のステートへ進む
                    user_data["location"] = match_location.group()
                    write_file(data_path2, user_data["location"])  # 場所をファイルに書き込む
                    
                    
                    # 応対メッセージ
                    message = (f'{user_data["location"]}は、今熱いところですね！\n\n')
                    if user_data["activity"] == "温泉ツアー":
                        message += f'先日、私の母も{user_data["location"]}は凄いと語ってくれました。\n\n'
                    elif user_data["activity"] == "遊園地ツアー":
                        message += '夜には今流行りのドローンショーが行われるだとか...。とても綺麗だと聞いております。\n\n'
                    elif user_data["activity"] == "バスツアー":
                        message += f'{user_data["location"]}おいしいものが沢山ありますので、食べ歩きしまくりましょう！\n\n'

                    message += 'それでは、ご希望の日付はいかがですか？（例: 2022/04/02 AM）'
                    state = 4  # 日時入力ステップへ進む
                    error_recovery = 0  # エラー回復カウンタをリセット
                else:
                    # 無効な入力があった場合
                    if(error_recovery == 0):
                        message = ( f'申し訳ありません、聞き取れませんでした。\n'
                                    f'もう一度お尋ねください。\n')                        
                    elif(error_recovery == 1):
                        message = ( f'「有馬温泉に行きたい！」という感じで聞いてください。\n')
                    else:
                        message = ( f'{activity_data[user_data["activity"]]}の中からお願いします。\n')
                                    
                    state = 3 # 場所入力ステップへ戻る
                    error_recovery += 1  # エラー回復カウンタをリセット
                    
            elif state == 4:
                # 課題5用　例: 形式に関係なく動作する、年月日の正規表現を追加                                
                # 予約可能性のチェックを入れる
                # 日付と時間の解析    
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  # 日付の正規表現（例: 2023/04/02）
                pattern_time = r'(AM|PM|am|pm|午前|午後)'  # 時間帯の正規表現
                
                # 入力文を正規表現で解析
                match_date = re.search(pattern_date, input)  # 日付を検索
                match_time = re.search(pattern_time, input)  # 時間帯を検索
                
                # 日時すべてが含まれている場合       
                    
                if match_date and match_time:
                    user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"
                    user_data["time"] = match_time.group().upper() if match_time else ''  # AM/PMがあるか確認
                    # ファイルに書き込む
                    write_file(data_path3, f'{user_data["date"]} {user_data["time"]}')
                    
                    # 予約内容を確認するメッセージ
                    message = (f'予約内容は、\n'
                               f'アクティビティ: {user_data["activity"]}\n'
                               f'場所: {user_data["location"]}\n'
                               f'日付: {user_data["date"]} {user_data["time"]}\n'
                               f'予算: {budget // 10000}万円\n'
                               'でよろしいですか？ (はい/いいえ)')
                    state = 5  # 次の確認ステップへ進む
                    error_recovery = 0  # エラー回復カウンタをリセット
                else:
                    if(error_recovery == 0):
                        message = ( f'申し訳ありません、聞き取れませんでした。\n'
                                    f'もう一度お願いします。\n')                    
                    elif(error_recovery == 1):
                        message = ( f'「2022年03月22日 午前でお願いします」という感じで聞いてください。\n')
                    else:
                        message = ( f' "年号・月・日・時刻"を決めていただけると助かります。\n')
                    
                    message = '正しい日付と時間を指定してください。'
                    state = 4 # 日時入力ステップへ戻る
                    error_recovery += 1 # エラー回復カウンタをリセット

            elif state == 5:
                if input == 'はい': 
                    try:
                        # user_data["date"]: YYYY/MM/DD形式でフォーマットされている
                        # user_data["time"]: AM/PM形式でフォーマットされている
                        year, month, day = map(int, user_data["date"].split('/'))
                        desired_date = datetime(year=int(year), month=int(month), day=int(day))
                        
                        date_time  = []
                        date_time.append([user_data["date"], user_data["time"]])
                        
                        printV("\n\n")
                        printV(booked_slots_per_location[user_data["location"]])
                        printV(user_data["date"])
                        printV(user_data["time"])
                        printV(date_time)
                        printV("\n\n")
                        
                        # 予約可能性のチェックを入れる
                        if desired_date < start_date or desired_date > end_date:
                            message = 'その日付は予約できません。'
                            state = 4                            
                        # date_time のすべての要素が location_time に含まれているかどうかを確認
                        # error例：elif date_time in booked_slots_per_location[user_data["location"]]: 
                        elif all(item in booked_slots_per_location[user_data["location"]] for item in date_time):   
                            message = f'{user_data["date"]}の{user_data["time"]}は予約が埋まっています。申し訳ありません。\n'
                            if desired_date.weekday() == 5 and user_data.weekday() == 6:
                                message += '土日は混雑が予想されますので、他の日程をご検討ください。\n'
                            else:
                                message += '他の日程をご検討ください。\n'
    
                            state = 4
                            attempt_count += 1
                        else:
                            message = f'予約いたしました。\n\n'
                            # 予約内容を確認するメッセージ                           
                            message += (
                                f'予約内容は、\n'
                                f'アクティビティ: {user_data["activity"]}\n'
                                f'場所: {user_data["location"]}\n'
                                f'日付: {user_data["date"]} {user_data["time"]}\n'
                                f'予算: {budget // 10000}万円\n'
                                'で予約が完了です、ありがとうございました。\n\n良い旅になることを心より願っております。')
                            attempt_count = 0  # リトライ成功時はカウントをリセット

                        # 予約不可の場合 (10回以上のリトライ)
                        if attempt_count >= max_attempts:
                            message = (f'{user_data["location"]}は只今とても混雑していまして、予約が困難な状況です。\n'
                                       f'他の場所をご検討いただくか、後ほど再度お尋ねいただけますでしょうか？お力になれず、申し訳ありませんでした。')
                            continueFlag = False
                            state = 1
                    
                    except ValueError as e:
                        message = (f'お聞きした日付が間違っている可能性があります: {e}\n'
                                   f'もう一度、希望日程をお聞きしてもよろしいでしょうか。')
                        state = 4
                
                elif input == 'いいえ':
                    message = '希望を取り消しました。もう一度お尋ねください。'
                    continueFlag = False
                    state = 1
                
       
            # 状態の更新
            write_file(data_path, int(state))
            write_file(data_path6, int(error_recovery))
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


