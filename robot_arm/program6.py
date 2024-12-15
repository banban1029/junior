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
            p = np.zeros(3) # 位置の初期化（単位：mm）
            p_achieved = np.zeros(3)
            
            # オフセット値の設定
            p_sets = np.array([
                [150, -100, 70],
                [0, 0, 100],
                [1000, 1000, 100]
            ])
            
            key = int(input("offset key:"))
            print()
            p = p_sets[key-1]
            
            # 1: theta[0]
                # ZeroDivisionError: float division by zero
            
            # 2: theta[2] cos(theta[3])が-1~1の範囲外
                # ValueError: math domain error
                           
          
            for i in range(3):                  # 6つの角度値を表示
                print(f"p{i+1}: {p[i]}")
            print()

            J = inverse_kinematics(p)
            p_achieved = forward_kinematics(J)
            
            z_check(p_achieved)
            
            error = np.fabs(p_sets[key-1] - p_achieved)
                
            for i in range(3):  # 6つの角度値を表示
                print(f"p{i+1}: {p_achieved[i]}, error: {error[i]}")
            print()
            
            moveto(J=J, marker_pos = p)

    except:
        traceback.print_exc()                   # try内で発生したエラーを表示
# -------------------- #


# ----- 学生定義のサブ関数（実験内容に応じてここに関数を追加する） ----- #

class Z_ERROR(Exception):
    pass

def z_check(p):
    if p[2] < 15.0:
        raise Z_ERROR('pz < 15.0 error')
    else:
        return True

def change_to_theta(J):
    theta = np.array([
        J[0] / 180 * np.pi,
        J[1] / 180 * np.pi + np.pi / 2,
        J[2] / 180 * np.pi,
        J[3] / 180 * np.pi + np.pi / 2,
        J[4] / 180 * np.pi - np.pi / 2,
        J[5] / 180 * np.pi
    ])
    return theta

def change_to_J(theta):
    J = np.array([
        180 * theta[0] / np.pi,
        180 * (theta[1] - np.pi / 2) / np.pi,
        180 * theta[2] / np.pi,
        180 * (theta[3] - np.pi / 2) / np.pi,
        180 * (theta[4] + np.pi / 2) / np.pi,
        180 * theta[5] / np.pi
    ])
    return J

def forward_kinematics(J):
    
    d = [d1, 0, 0, d4, d5, d6]
    theta = change_to_theta(J) 
    l = [0, a2, a3, 0, 0, 0]
    alpha = [pi/2, 0, 0, pi/2, pi/2, 0]
    
    A = cos(theta[3])*sin(theta[4])*d[5] + sin(theta[3])*d[4]
    B = -sin(theta[3])*sin(theta[4])*d[5] + cos(theta[3])*d[4]
    E = d[3] - cos(theta[4])*d[5]
    H = d[0]
    I = l[2]*cos(theta[1])*sin(theta[2])
    
    px = A*cos(theta[0])*cos(theta[1]+theta[2]) + B*cos(theta[0])*sin(theta[1]+theta[2]) + (l[1]+l[2]*cos(theta[2]))*cos(theta[0])*cos(theta[1]) + E*sin(theta[0]) -l[2]*cos(theta[0])*sin(theta[1])*sin(theta[2])
    
    py = A*sin(theta[0])*cos(theta[1]+theta[2]) + B*sin(theta[0])*sin(theta[1]+theta[2]) + (l[1]+l[2]*cos(theta[2]))*sin(theta[0])*cos(theta[1]) - E*cos(theta[0]) - l[2]*sin(theta[0])*sin(theta[1])*sin(theta[2])
    
    pz = A*sin(theta[1]+theta[2]) - B*cos(theta[1]+theta[2]) + (l[1]+l[2]*cos(theta[2]))*sin(theta[1]) + H + I
    
    p = np.array([px, py, pz])

    return p

def inverse_kinematics(p):
    J = np.zeros(6)
    d = [d1, 0.0, 0.0, d4, d5, d6] 
    theta = np.zeros(6)   
    l = [0.0, a2, a3, 0.0, 0.0, 0.0]
    alpha = [pi/2, 0.0, 0.0, pi/2, pi/2, 0.0]
    
    px, py, pz = p
    
    "theta1"
    if py > 0:
        theta[0] = pi - atan2(px, py) - acos(d[3]/sqrt(px*px + py*py))
    else:
        theta[0] = pi/2 + atan2(py, px) - acos(d[3]/sqrt(px*px + py*py))
        
        
    "極座標変換"
    X = (px - cos(theta[0])*d[4] - sin(theta[0])*d[3])/cos(theta[0])
    Z = pz - d[0] + d[5]

    r = sqrt(X*X + Z*Z)
    r_alpha = atan2(Z, X)
    
    h = sqrt(l[1]*l[1] + l[2]*l[2] + 2*l[1]*l[2]*cos(theta[1]))
    h_beta = atan2(l[2]*sin(theta[1]), l[1] + l[2]*cos(theta[1]))
        
    "theta3"
    theta[2] = -atan2(sqrt((r*r+l[1]*l[1]+l[2]*l[2])**2 - 2*(r**4 + l[1]**4 + l[2]**4)), (r*r-l[1]*l[1]-l[2]*l[2]))
    # theta[2] = -atan2(sqrt(4*l[1]*l[1]*l[2]*l[2]-(r*r-l[1]*l[1]-l[2]*l[2])*(r*r-l[1]*l[1]-l[2]*l[2])), r*r-l[1]*l[1]-l[2]*l[2])
    
    "theta2"
    theta[1] = atan2(Z, X) - atan2(l[2]*sin(theta[2]), l[1] + l[2]*cos(theta[2]))
    
    "theta4"
    theta[3] = pi/2 - theta[1] - theta[2]
    
    "theta5"
    theta[4] = - pi/2
    
    "theta6"
    theta[5] = theta[0]
    
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
