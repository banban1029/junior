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

# 環境変数設定
start_date = datetime(2022, 3, 1) # 予約開始期間
end_date = datetime(2022, 4, 30) # 予約終了期間


# activity_dataの読み込み
activity_data = {
    "温泉ツアー": ["登別", "有馬", "別府", "草津", "白浜"],
    "遊園地ツアー": ["USJ", "ディズニーランド", "ディズニーシー", "花やしき", "ひらかたパーク"],
    "バスツアー": ["中華街", "黒潮市場", "姫路城"]
}

# budget_dataの読み込み
budget_data = {
    "登別": 130000, "有馬": 50000, "別府": 100000, "草津": 70000, "白浜": 50000,
    "USJ": 30000, "ディズニーランド": 50000, "ディズニーシー": 50000, "花やしき": 40000, "ひらかたパーク": 10000,
    "中華街": 15500, "黒潮市場": 15500, "姫路城": 10000
}

# user_dataの初期化
user_data = {
    "activity": None,
    "location": None,
    "date": None,
    "time": None # 課題5　時間の追加 (より柔軟な入力を受け付ける)
}

@app.route('/', methods=['POST'])
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
    data_path6 = os.getcwd() + '/booked_slots.txt'  # 予約済みスロットを保存用
    data_path7 = os.getcwd() + '/error_recovery.txt' # エラー回避援助のためのカウンタ
    
    # data所得
    state = read_file(data_path, 'int', 1)
    user_data["activity"] = read_file(data_path1, 'str', None)
    user_data["location"] = read_file(data_path2, 'str', None)
    # 課題5 日程所得 ("YYYY/MM/DD TIME" 形式)、 空白でトリミングして分割
    user_data["date"], user_data["time"] = read_file(data_path3, 'str', "None None").strip().split()  
    attempt_count = read_file(data_path4, 'int', 0)
    error_recovery = read_file(data_path7, 'int', 0)
    budget = budget_data.get(user_data["location"], 0)
    
    # 初期状態の場合、予約状況スロットを生成
    if(state == 1):
        available_slots, booked_slots = distribution_slots()
        # 予約状況をファイルに保存
        save_slots_to_file(data_path5, available_slots)
        save_slots_to_file(data_path6, booked_slots)
        
        # 読み込んだデータを確認
        print_booked_slots(booked_slots, available_slots, activity_data)
        
    # 予約スロット生成（ルール適用）および予約状況の管理
    available_slots = {}
    booked_slots = {}
    
    # スロットを読み込む
    available_slots = load_slots_from_file(data_path5)
    booked_slots = load_slots_from_file(data_path6)
    
    printV(available_slots)
    printV(booked_slots)
    
    # リトライ回数の設定
    max_attempts = 10 
    ######################################################################################
    
    if input == 'バイバイ':  # 会話を終了するメッセージ「バイバイ」を受け取った場合
        message = 'ありがとうございました。またのご利用をお待ちしております。'
        continueFlag = False
    else:  # 通常のメッセージを受け取った場合
            
        ###########################################################
        if input == 'リセット':  # 状態をリセットする場合
            state = 1
            message = '状態をリセットしました'
            continueFlag = False
        ###########################################################
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
        ########################################################### 
        else:    
            # 状態に応じて異なる発話を生成
            if state == 1:
                message = 'どのアクティビティをご希望ですか？\n'
                state = 2
                error_recovery = 0  # エラー回復カウンタをリセット
            
            # activity選択
            elif state == 2:   
                # 課題5　柔軟な入力を受け付ける(正規表現)
                # 複数入力、keyword抽出
                pattern_activity = r'(温泉|遊園地|バス)'  
                pattern_location = r'|'.join([re.escape(location) for locations in activity_data.values() for location in locations]) 
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  
                pattern_time = r'(AM|PM|am|pm|午前|午後)'  
                
                # 入力文を正規表現で解析
                match_activity = re.search(pattern_activity, input)  
                match_location = re.search(pattern_location, input) 
                match_date = re.search(pattern_date, input)  
                match_time = re.search(pattern_time, input)  
                
                # keyword抽出が適応された場合
                if match_activity and match_location and match_date and match_time:
                    # アクティビティ、場所、日時すべてが含まれている場合
                    user_data["activity"] = match_activity.group() + "ツアー"
                    user_data["location"] = match_location.group()
                    user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"  # YYYY/MM/DD形式でフォーマット
                    user_data["time"] = match_time.group().upper() if match_time else ''  # AM/PMがあるか確認
                    budget = budget_data.get(user_data["location"], 0)

                    # data書き出し
                    write_file(data_path1, user_data["activity"])
                    write_file(data_path2, user_data["location"])
                    write_file(data_path3, f'{user_data["date"]} {user_data["time"]}')
                               
                    # 予約内の確認
                    message = (f'予約内容は、\n'
                               f'アクティビティ: {user_data["activity"]}\n'
                               f'場所: {user_data["location"]}\n'
                               f'日付: {user_data["date"]} {user_data["time"]}\n'
                               f'予算: {budget // 10000}万円\n'
                               'でよろしいですか？ (はい/いいえ)')
                    state = 5  # 予約ステップへ進む
                    error_recovery = 0  # エラー回復カウンタをリセット
                        
                elif match_activity and match_location:
                    # activityとlocationが入力されている場合 -> 日時指定のステートへ進む
                    user_data["activity"] = match_activity.group() + "ツアー"
                    user_data["location"] = match_location.group()
                    # data書き出し
                    write_file(data_path1, user_data["activity"])  
                    write_file(data_path2, user_data["location"])   
                    
                    # 応対メッセージ                       
                    message = 'ご希望の日程はいかがなさいますか。'
                    state = 4  # 日時入力ステップへ進む
                    printV(booked_slots[user_data["location"]])
                    error_recovery = 0  # エラー回復カウンタをリセット

                elif match_activity:
                    # activityのみ入力された場合
                    user_data["activity"] = match_activity.group() + "ツアー"
                    
                    # data書き出し
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
                    # 課題5　エラーリカバリー                     
                    elif (error_recovery == 1): 
                        message = ( f'「温泉にゆったりつかりたい！」という感じで聞いてください\n')
                    else:
                        message = ( f'「温泉ツアー」・「遊園地ツアー」・「バスツアー」の中からお選びください。\n')
                    
                    state = 2  # activity入力ステップへ戻る
                    error_recovery += 1 # エラー回復カウンタを+1
                                
            # locationの選択              
            elif state == 3:
                # 課題5　柔軟な入力を受け付ける(正規表現)
                # 複数入力、keyword抽出
                #'登別|有馬|別府|草津|白浜|USJ|ディズニーランド|ディズニーシー|花やしき|ひらかたパーク|中華街|黒潮市場|姫路城'                
                pattern_location = r'|'.join([re.escape(location) for locations in activity_data.values() for location in locations])  # 場所の正規表現
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  
                pattern_time = r'(AM|PM|am|pm|午前|午後)' 
                
                # 入力文を正規表現で解析
                match_location = re.search(pattern_location, input)  
                match_date = re.search(pattern_date, input)  
                match_time = re.search(pattern_time, input) 
                
                
                if match_location and match_date and match_time:
                    
                    #  activity, location, date, time がすべて含まれている場合
                    user_data["location"] = match_location.group()
                    user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"  # YYYY/MM/DD形式でフォーマット
                    user_data["time"] = match_time.group().upper() if match_time else ''  
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
                    
                    # locationのみ入力された場合
                    user_data["location"] = match_location.group()
                    
                    # ファイルに書き込む
                    write_file(data_path2, user_data["location"])  
                    
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
                    # 課題5　エラーリカバリー                    
                    elif(error_recovery == 1):
                        message = ( f'「有馬温泉に行きたい！」という感じで聞いてください。\n')
                    else:
                        message = ( f'{activity_data[user_data["activity"]]}の中からお願いします。\n')
                                    
                    state = 3 # 場所入力ステップへ戻る
                    error_recovery += 1  # エラー回復カウンタをリセット
            
            # date, timeの選択    
            elif state == 4:
                # 課題5　例: 形式に関係なく動作する、年月日の正規表現を追加                                
                pattern_date = r'(\d{4})[^\d]?(\d{1,2})[^\d]?(\d{1,2})[^\d]?'  
                pattern_time = r'(AM|PM|am|pm|午前|午後)'  
                
                # 入力文を正規表現で解析
                match_date = re.search(pattern_date, input)  
                match_time = re.search(pattern_time, input) 
                  
                if match_date and match_time:
                    
                    # date, time が入力された場合
                    user_data["date"] = f"{match_date.group(1)}/{match_date.group(2).zfill(2)}/{match_date.group(3).zfill(2)}"
                    user_data["time"] = match_time.group().upper() if match_time else ''  
                    
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
                    # 課題5　エラーリカバリー              
                    elif(error_recovery == 1):
                        message = ( f'「2022年03月22日 午前でお願いします」という感じで聞いてください。\n')
                    else:
                        message = ( f' "年号・月・日・時刻"を決めていただけると助かります。\n')
                    
                    message = '正しい日付と時間を指定してください。'
                    state = 4 # 日時入力ステップへ戻る
                    error_recovery += 1 # エラー回復カウンタをリセット

            # 予約内容の確認
            elif state == 5:
                
                if input == 'はい': 
                    try:
                        # user_data["date"]: YYYY/MM/DD形式でフォーマット
                        # user_data["time"]: AM/PM形式でフォーマット
                        # 日程の確認・比較用
                        year, month, day = map(int, user_data["date"].split('/'))
                        desired_date = datetime(year=int(year), month=int(month), day=int(day))
                        
                        date_time  = []
                        date_time.append([user_data["date"], user_data["time"]])
                        
                        # 予約可能な日付かどうかを確認
                        if desired_date < start_date or desired_date > end_date:
                            message = 'その日付は予約できません。'
                            state = 4  # 日時入力ステップへ戻る 
                                                     
                        # 予約状況の照合
                        elif all(item in booked_slots[user_data["location"]] for item in date_time):  
                            # 予約不可の場合 
                            message = f'{user_data["date"]}の{user_data["time"]}は予約が埋まっています。申し訳ありません。\n'
                            if desired_date.weekday() == 5 and user_data.weekday() == 6:
                                message += '土日は混雑が予想されますので、他の日程をご検討ください。\n'
                            else:
                                message += '他の日程をご検討ください。\n'
    
                            state = 4 # 日時入力ステップへ戻る
                            attempt_count += 1 # リトライ回数を+1
                        else:
                            # 予約可能な場合
                            message = f'予約いたしました。\n\n'                          
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
    write_file(data_path4, attempt_count)
    write_file(data_path7, int(error_recovery))
    
            
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


# 稼働日の取得
def generate_slots_with_rules(activity):
    global start_date
    global end_date
    
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

# 割合選出関数
def generate_booked_slots(available_slots, rate):
    booked_count = int(len(available_slots) * rate)
    booked_slots = random.sample(available_slots, booked_count)  # ランダムな予約済みスロットを選択
    return booked_slots

# 予約スロットを生成
def distribution_slots():
    
    global activity_data
    global budget_data
    global start_date
    global end_date
    
    available_slots = {}
    booked_slots = {}
    
    for activity, locations in activity_data.items():
        for location in locations:
            
            # activityごとの予約可能スロットの生成
            available_slots[location] = generate_slots_with_rules(activity)

            # 予約済みスロットの割合を設定
            if activity == "温泉ツアー":
                # 土曜日の午後:予約済み割合0.8
                saturday_pm_slots = [slot for slot in available_slots[location] if datetime.strptime(slot[0], "%Y/%m/%d").weekday() == 5 and slot[1] == "PM"]
                booked_saturday_pm_slots = generate_booked_slots(saturday_pm_slots, 0.6)
                
                # 土曜日午後以外:予約済み割合0.4
                other_slots = [slot for slot in available_slots[location] if not (datetime.strptime(slot[0], "%Y/%m/%d").weekday() == 5 and slot[1] == "PM")]
                booked_other_slots = generate_booked_slots(other_slots, 0.4)

                # スロット結合
                booked_slots[location] = booked_saturday_pm_slots + booked_other_slots

            elif activity == "遊園地ツアー":
                if location in ["USJ", "ディズニーランド", "ディズニーシー"]:  # 混雑しやすい遊園地
                    # 平日:予約済み割合0.6
                    weekday_slots = [slot for slot in available_slots[location] if datetime.strptime(slot[0], "%Y/%m/%d").weekday() < 5]  
                    booked_weekday_slots = generate_booked_slots(weekday_slots, 0.6) 
                    
                    # 週末:予約済み割合0.8
                    weekend_slots = [slot for slot in available_slots[location] if datetime.strptime(slot[0], "%Y/%m/%d").weekday() >= 5]  
                    booked_weekend_slots = generate_booked_slots(weekend_slots, 0.8) 
                    
                    # スロット結合
                    booked_slots[location] = booked_weekday_slots + booked_weekend_slots
                else:
                    # 平日:予約済み割合0.4
                    weekday_slots = [slot for slot in available_slots[location] if datetime.strptime(slot[0], "%Y/%m/%d").weekday() < 5]  
                    booked_weekday_slots = generate_booked_slots(weekday_slots, 0.4) 
                    
                    # 週末:予約済み割合0.5
                    weekend_slots = [slot for slot in available_slots[location] if datetime.strptime(slot[0], "%Y/%m/%d").weekday() >= 5]  
                    booked_weekend_slots = generate_booked_slots(weekend_slots, 0.5) 
                    
                    # スロット結合
                    booked_slots[location] = booked_weekday_slots + booked_weekend_slots

            elif activity == "バスツアー":
                # 平日:予約済み割合0.2
                booked_slots[location] = generate_booked_slots(available_slots[location], 0.2)
  
    return available_slots, booked_slots

# スロットをファイルに保存する関数
def save_slots_to_file(file_name, booked_slots_per_location):
    with open(file_name, 'w') as f:
        json.dump(booked_slots_per_location, f, ensure_ascii=False, indent=4)


# スロットをファイルから読み込む関数
def load_slots_from_file(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

# 予約スケジュールの可視化関数
def print_booked_slots(available_slots, booked_slots):
    global activity_data
    global budget_data
    
    for activity, locations in activity_data.items():
        print(f"アクティビティ: {activity}")
        print("=" * 40)
        for location in locations:
            print(f"場所: {location}")
            print("-" * 30) 
            # 予約済みスロットの出力
            print("予約済みスロット:")
            # booked_slots = booked_slots_per_location.get(location, [])
            if booked_slots[location]:
                for slot in booked_slots[location]:
                    date, time = slot
                    print(f"  日付: {date}, 時間帯: {time}")
            else:
                print("  予約済みスロットはありません。")
            # 予約可能スロットの出力
            print("\n予約可能スロット:")
            # available_slots = available_slots_per_location.get(location, [])
            if available_slots:
                for slot in available_slots:
                    date, time = slot
                    if slot not in booked_slots:
                        print(f"  日付: {date}, 時間帯: {time}")
            else:
                print("  予約可能なスロットはありません。")
            print("\n" + "=" * 30 + "\n")

# ファイル読み込み関数
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

# ファイル書き出し関数
def write_file(filepath, content): 
    if glob.glob(filepath):  # .txtが見つかった場合
        printV(filepath + ' is found!')
        with open(filepath, mode='w', encoding='utf-8') as w:
            w.write(str(content))
            return content
    else:  # .txtが見つからなかった場合
        printV(filepath + ' is not found!')
        printV('Error:')