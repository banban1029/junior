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

            J = np.zeros(6)  # 角度値の初期化（単位：degree）
                       
            p_sets = np.array([
                [150, -100, 70],  # p_object
                [150, 100, 70]    # p_target
            ]) 

            for p in p_sets:
                J = inverse_kinematics(p)
                moveto(J=J, marker_pos=p)         

    except:
        traceback.print_exc()                   # try内で発生したエラーを表示
# -------------------- #


# ----- 学生定義のサブ関数（実験内容に応じてここに関数を追加する） ----- #

def change_to_J(theta):
    J = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    J[0] = 180*theta[0]/pi
    J[1] = 180*(theta[1]-pi/2)/pi
    J[2] = 180*theta[2]/pi
    J[3] = 180*(theta[3]-pi/2)/pi
    J[4] = 180*(theta[4]+pi/2)/pi
    J[5] = 180*theta[5]/pi
    
    return J

class atan2Error(Exception):
    pass

class sqrtError(Exception):
    pass

def atan2_check(y,x):
    if x <= 0.001 and x >= -0.001:
        raise atan2Error('atan2 error')
    return atan2(y,x)

def sqrt_check(x):
    if x < 0:
        raise sqrtError('sqrt error')
    return sqrt(x)


def inverse_kinematics(p):
    d = [d1, 0, 0, d4, d5, d6]    
    l = [0, a2, a3, 0, 0, 0]
    alpha = [pi/2, 0, 0, pi/2, pi/2, 0]
    
    J = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    theta = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    px = p[0]
    py = p[1]
    pz = p[2]
    
    "極座標変換"
    X = (px - cos(theta[0])*d[4] - sin(theta[0])*d[3])/cos(theta[0])
    Z = pz - d[0] + d[5]

    r = sqrt_check(X*X + Z*Z)
    r_alpha = atan2_check(Z, X)
    
    h = sqrt_check(l[1]*l[1] + l[2]*l[2] + 2*l[1]*l[2]*cos(theta[1]))
    h_beta = atan2_check(l[2]*sin(theta[1]), l[1] + l[2]*cos(theta[1]))
    
    
    "theta1"
    if py > 0:
        theta[0] = pi - atan2_check(px, py) - acos(d[3]/sqrt(px*px + py*py))
    else:
        theta[0] = pi/2 + atan2_check(py, px) - acos(d[3]/sqrt(px*px + py*py))
        
        
    "theta3"
    print("sqrt",(r*r+l[1]*l[1]+l[2]*l[2])**2 - 2*(r**4 + l[1]**4 + l[2]**4))
    
    theta[2] = -atan2_check(sqrt_check((r*r+l[1]*l[1]+l[2]*l[2])**2 - 2*(r**4 + l[1]**4 + l[2]**4)), r*r-l[1]*l[1]-l[2]*l[2])
    
    
    theta[1] = atan2_check(Z, X) - atan2_check(l[2]*sin(theta[2]), l[1] + l[2]*cos(theta[2]))
    
    "theta4"
    theta[3] = pi/2 - theta[1] - theta[2]
    
    "theta5"
    theta[4] = - pi/2
    
    "theta6"
    theta[5] = theta[0]
    
    for i in range(6):                  # 6つの角度値を表示
        print("theta"+str(i+1)+": ",theta[i])
    
    J = change_to_J(theta)
    
    return J
    
    
    
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
