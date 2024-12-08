from math import acos, pi, atan2, sqrt, degrees

# アーム手先位置
px = 100
py = 150

# - リンク長の定義 [mm] - #
d1 = 140
a2 = 110.4
a3 = 96.0
d4 = 66.39
d5 = 73.18
d6 = 43.6

d = [d1, 0, 0, d4, d5, d6]

### theta1の計算をここに記入 ###
theta1 = pi - atan2(px, py) - acos(d[3]/sqrt(px*px + py*py))
#############################

# theta1 -> J1に変換
J1 = degrees(theta1)

print("theta1: ", J1)