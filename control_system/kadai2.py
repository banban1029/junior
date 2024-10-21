import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# 定数の定義
l = 0.0745  # 重心までの距離
r = 0.021  # 車輪半径
m = 0.0053  # 車輪重量
M = 0.15  # 本体重量
Jw = 1.16e-6  # 車輪慣性モーメント
Jb = 6.93e-5  # 本体慣性モーメント
g = 9.8  # 重力加速度
c = 4.91e-7  # 軸粘性摩擦係数
eta = 0.75  # 駆動系の効率
i = 21  # ギア比
Kt = 0.00115  # モータトルク定数

# 行列の定義
alpha = np.array([[M*l**2 + Jb, M*r*l], [M*r*l, (m+M)*r**2 + Jw]])
beta = np.array([[c, 0], [0, 0]])
ganma = np.array([[-M*g*l, 0], [0, 0]])
delta = np.array([[1, 0], [0, 1]])

# 初期条件と時間の設定
x0 = [math.pi / 6, 0, 0, 0.1]  # [phi, theta, dphi, dtheta] の初期値
t = np.linspace(0, 5, 500)  # 0秒から10秒までを1000ステップでシミュレーション
u = np.array([[0], [eta * i * Kt]])  # 入力（モータトルク）



def kadai2(A, B):
    # 固有値と固有ベクトルの計算
    eigenvalues, eigenvectors = np.linalg.eig(A)
    
    #　積の計算
    AB = A @ B
    AAB = A @ A @ B
    AAAB = A @ A @ A @ B
    
    # 可制御性の判定
    Mc = np.hstack([B, AB, AAB, AAAB])
    rank_Mc = np.linalg.matrix_rank(Mc)

    # 固有値と固有ベクトルを出力
    # print("\nA:\n", A)
    # print("\nB:\n", B)
    # print("行列 A の固有値:")
    # print(eigenvalues, "\n")
    # print("\n行列 A の固有ベクトル:")
    # print(eigenvectors, "\n")
    # print("B:\n", B)
    # print("\nAB:\n", AB)
    # print("\nAAB:\n", AAB)
    # print("\nAAAB:\n", AAAB) 
    # print('\nrank(Mc) =', rank_Mc) 
        
    if rank_Mc == 4:
        return True
    else:
        return False


# 状態方程式の定義
def equations(x0, t, u, feedback=False):
    phi, theta, dphi, dtheta = x0

    # 行列 A と B の定義
    A = np.block([
        [np.zeros((2, 2)), np.eye(2)],
        [-np.linalg.inv(alpha) @ ganma, -np.linalg.inv(alpha) @ beta]
    ])
    
    B = np.vstack([np.zeros((2, 2)), -np.linalg.inv(alpha) @ delta])

    # 状態変数ベクトル x
    x = np.array([[phi], [theta], [dphi], [dtheta]])
    
    
    # フィードバック制御の計算
    if feedback and kadai2(A, B):
        # 必要な極の設定
        desired_poles = np.array([-5, -2.5, -1, -3.5])  # 極の配置
        
        # コントローラ設計
        xi1 = np.array([[1], [0]])
        xi2 = np.array([[0], [1]])
        xi3 = np.array([[1], [1]])
        xi4 = np.array([[1], [1]])
        
        v1 = np.linalg.inv(A - desired_poles[0] * np.eye(4)) @ B @ xi1
        v2 = np.linalg.inv(A - desired_poles[1] * np.eye(4)) @ B @ xi2
        v3 = np.linalg.inv(A - desired_poles[2] * np.eye(4)) @ B @ xi3
        v4 = np.linalg.inv(A - desired_poles[3] * np.eye(4)) @ B @ xi4
        
        V = np.hstack([v1, v2, v3, v4])
        
        # Vが正則であるかどうかを判定
        if np.linalg.matrix_rank(V) == V.shape[0]:  # 行数が等しいか確認
            count = 0
            if count!=0:
                print("\nVは正則です\n")
                
        else:
            print("\nVは正則ではありません\n")
            return None  # ここでNoneを返して関数を終了
        
        Xi = np.hstack([xi1, xi2, xi3, xi4])
        K = -Xi @ np.linalg.inv(V)

        # 状態方程式 dx = (A - B*K)x + B*u
        dx = (A - B @ K) @ x + B @ u
    else:
        # 通常の状態方程式
        dx = A @ x + B @ u
        
    # デバッグ情報
    # print("Current State:", x.flatten())
    print("Next State:", dx.flatten())
    # print("\n\nFeedback x:", x)
    print("\n\nFeedback dx:", dx)
    
    
#     Next State: [ 1.76109947e+105 -1.17218618e+105  8.42965767e+106 -5.61077236e+106]


# Feedback dx: [[ 1.76109947e+105]
#  [-1.17218618e+105]
#  [ 8.42965767e+106]
#  [-5.61077236e+106]]



    return dx.flatten()

# 数値解を計算
sol_no_feedback = odeint(equations, x0, t, args=(u, False))  # フィードバックなし
sol_with_feedback = odeint(equations, x0, t, args=(u, True))  # フィードバックあり



# プロットの設定
plt.figure(figsize=(10, 10))  # 図全体のサイズを設定

# フィードバックなしのサブプロット
plt.subplot(2, 1, 1)  # 2行1列の1番目のプロット
plt.plot(t, sol_no_feedback[:, 0], label='phi (angle) - No Feedback', color='b')
plt.plot(t, sol_no_feedback[:, 1], label='theta (angle) - No Feedback', color='r')
plt.xlabel('Time [s]')
plt.ylabel('Angle [rad]')
plt.title('System Response Without Feedback')
plt.legend()
plt.grid()


# フィードバックありのサブプロット
plt.subplot(2, 1, 2)  # 2行1列の2番目のプロット
plt.plot(t, sol_with_feedback[:, 0], label='phi (angle) - With Feedback', color='g', linestyle='--')
plt.plot(t, sol_with_feedback[:, 1], label='theta (angle) - With Feedback', color='orange', linestyle='--')
plt.xlabel('Time [s]')
plt.ylabel('Angle [rad]')
plt.title('System Response With Feedback')
plt.legend()
plt.grid()




# 最後に全体を表示
plt.tight_layout()  # レイアウトを調整
plt.show()










# plt.figure(figsize=(10, 5))
# plt.plot(t, sol_no_feedback[:, 0], label='phi (angle) - No Feedback', color='b')
# plt.plot(t, sol_no_feedback[:, 1], label='theta (angle) - No Feedback', color='r')
# plt.plot(t, sol_with_feedback[:, 0], label='phi (angle) - With Feedback', color='g', linestyle='--')
# plt.plot(t, sol_with_feedback[:, 1], label='theta (angle) - With Feedback', color='orange', linestyle='--')
# plt.xlabel('Time [s]')
# plt.ylabel('Angle [rad]')
# plt.legend()
# plt.title('System Response with and without Feedback')
# plt.grid()
# plt.show()
