import time
from math import radians,degrees,sin,cos,atan2,sqrt,pi,acos
import traceback
import numpy as np

print("mode select:")
print("* 0 -> value check")
print("* 1 -> simulation")
print("* 2 -> move mode")
move_mode = int(input())


# ----- メイン関数 ----- #
def main():

    print("start program")

    try:    # try内で何らかのエラーが発生 -> 処理中断してexceptに移動

        # --- メインループ （実験内容に応じてここを変更）--- #
        while True:

            J = np.zeros(6) # 角度値の初期化（単位：degree）
            
            for i in range(6):
                print("input J["+str(i)+"]:")
                J[i] = float(input())               # 角度値をキーボード入力
                
            for i in range(6):                  # 6つの角度値を表示
                print("J"+str(i+1)+": ",J[i])

            moveto(J=J, marker_pos = [100, 100, 100])

    except:
        traceback.print_exc()                   # try内で発生したエラーを表示
# -------------------- #


# ----- 学生定義のサブ関数（実験内容に応じてここに関数を追加する） ----- #

# ------------------------------------------------------------ #

# ----- 【！変更しないこと！】mycobotライブラリの初期化 ----- #

if move_mode==1:
    from mycobot_sim import send_angles_sim

elif move_mode==2:
    print("load mycobot library...", end=" ")
    from pymycobot.mycobot import MyCobot
    from pymycobot.genre import Angle
    from pymycobot import PI_PORT, PI_BAUD

    mycobot = MyCobot(PI_PORT, PI_BAUD)
    time.sleep(1)
    mycobot.set_gripper_ini()
    time.sleep(1)
    print("OK")


# - 【！変更しないこと！】リンク長の定義 [mm] - #
d1 = 140
a2 = 110.4
a3 = 96.0
d4 = 66.39
d5 = 73.18
d6 = 43.6


# ----- 【！変更しないこと！】mycobot6軸関節確度制御----- #
def moveto(J, marker_pos):

    angle_check(J)  # 角度が動作範囲内かチェック

    if move_mode == 2:
        print("move")
        mycobot.send_angles([J[0]-90, J[1], J[2], J[3], J[4], J[5]], 20)
        time.sleep(5)

    elif move_mode == 1:
        send_angles_sim(J=J, marker_pos=marker_pos)


# ----- 【！変更しないこと！】角度リミットエラー用 ----- #
class AngleError(Exception):
    pass


# ----- 【！変更しないこと！】関節角度範囲チェック ----- #
def angle_check(J):

    print("angle_check...", end=" ")

    if J[0] < -90 or J[0] > 90:
        raise AngleError('J1 angle error')

    if J[1] < -120 or J[1] > 120:
        raise AngleError('J2 angle error')

    if J[2] < -150 or J[2] > 150:
        raise AngleError('J3 angle error')

    if J[3] < -120 or J[3] > 120:
        raise AngleError('J4 angle error')

    if J[4] < -120 or J[4] > 120:
        raise AngleError('J5 angle error')

    if J[5] < -90 or J[5] > 90:
        raise AngleError('J6 angle error')

    print("OK\n")

# ----- 【！変更しないこと！】メイン処理 ----- #
if __name__ == "__main__":
    main()
