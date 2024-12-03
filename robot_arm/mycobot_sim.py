"""
Class of n-link arm in 3D
Author: Takayuki Murooka (takayuki5168)
Reference: https://github.com/AtsushiSakai/PythonRobotics
"""
import numpy as np
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

PLOT_AREA = 0.5*1000


class Link:
    def __init__(self, dh_params):
        self.dh_params_ = dh_params

    def transformation_matrix(self):
        # theta = self.joint_angle_
        theta = self.dh_params_[0]
        alpha = self.dh_params_[1]
        a = self.dh_params_[2]
        d = self.dh_params_[3]

        st = math.sin(theta)
        ct = math.cos(theta)
        sa = math.sin(alpha)
        ca = math.cos(alpha)
        trans = np.array([[ct, -st * ca, st * sa, a * ct],
                          [st, ct * ca, -ct * sa, a * st],
                          [0, sa, ca, d],
                          [0, 0, 0, 1]])

        return trans




class NLinkArm:
    def __init__(self, dh_params_list):
        self.link_list = []
        for i in range(len(dh_params_list)):
            self.link_list.append(Link(dh_params_list[i]))

    @staticmethod
    def convert_joint_angles_sim_to_mycobot(joint_angles):
        """convert joint angles simulator to mycobot

        Args:
            joint_angles ([float]): [joint angles(radian)]

        Returns:
            [float]: [joint angles calculated(radian)]
        """
        conv_mul = [-1.0, -1.0, 1.0, -1.0, -1.0, -1.0]
        conv_add = [0.0, -math.pi / 2, 0.0, -math.pi / 2, math.pi / 2, 0.0]

        joint_angles = [joint_angles * conv_mul for (joint_angles, conv_mul) in zip(joint_angles, conv_mul)]
        joint_angles = [joint_angles + conv_add for (joint_angles, conv_add) in zip(joint_angles, conv_add)]

        joint_angles_lim = []
        for joint_angle in joint_angles:
            while joint_angle > math.pi:
                joint_angle -= 2 * math.pi

            while joint_angle < -math.pi:
                joint_angle += 2 * math.pi

            joint_angles_lim.append(joint_angle)

        return joint_angles_lim

    def transformation_matrix(self):
        trans = np.identity(4)
        for i in range(len(self.link_list)):
            trans = np.dot(trans, self.link_list[i].transformation_matrix())
        return trans

    def forward_kinematics(self, plot=False, marker_pos=[0, 0, 0]):
        trans = self.transformation_matrix()

        x = trans[0, 3]
        y = trans[1, 3]
        z = trans[2, 3]
        alpha, beta, gamma = self.euler_angle()

        if plot:
            self.fig = plt.figure()
            self.ax = Axes3D(self.fig)
            self.fig.add_axes(self.ax)

            x_list = []
            y_list = []
            z_list = []

            trans = np.identity(4)

            x_list.append(trans[0, 3])
            y_list.append(trans[1, 3])
            z_list.append(trans[2, 3])
            for i in range(len(self.link_list)):
                trans = np.dot(trans, self.link_list[i].transformation_matrix())
                x_list.append(trans[0, 3])
                y_list.append(trans[1, 3])
                z_list.append(trans[2, 3])

            self.ax.set_xlabel("x [mm]", size=12)
            self.ax.set_ylabel("y [mm]", size=12)
            self.ax.set_zlabel("z [mm]", size=12)

            self.ax.plot(x_list, y_list, z_list, "o-", color="#00aa00", ms=4,
                         mew=0.5)
            self.ax.plot([0], [0], [0], "o")
            self.ax.plot([marker_pos[0]], [marker_pos[1]], [marker_pos[2]], "o")

            self.ax.set_xlim(-PLOT_AREA/2, PLOT_AREA/2)
            self.ax.set_ylim(-PLOT_AREA/2, PLOT_AREA/2)
            self.ax.set_zlim(0.0, PLOT_AREA)

            plt.show()

        return [x, y, z, alpha, beta, gamma]



    def euler_angle(self):
        trans = self.transformation_matrix()

        alpha = math.atan2(trans[1][2], trans[0][2])
        if not (-math.pi / 2 <= alpha <= math.pi / 2):
            alpha = math.atan2(trans[1][2], trans[0][2]) + math.pi
        if not (-math.pi / 2 <= alpha <= math.pi / 2):
            alpha = math.atan2(trans[1][2], trans[0][2]) - math.pi
        beta = math.atan2(
            trans[0][2] * math.cos(alpha) + trans[1][2] * math.sin(alpha),
            trans[2][2])
        gamma = math.atan2(
            -trans[0][0] * math.sin(alpha) + trans[1][0] * math.cos(alpha),
            -trans[0][1] * math.sin(alpha) + trans[1][1] * math.cos(alpha))

        return alpha, beta, gamma

    def send_angles(self, joint_angle_list):
        for i in range(len(self.link_list)):
            self.link_list[i].dh_params_[0] = joint_angle_list[i]

    def update_joint_angles(self, diff_joint_angle_list):
        for i in range(len(self.link_list)):
            self.link_list[i].dh_params_[0] += diff_joint_angle_list[i]

    def get_angles(self):
        joint_angles = []
        for i in range(len(self.link_list)):
            joint_angle = self.link_list[i].dh_params_[0]
            while joint_angle > math.pi:
                joint_angle -= 2 * math.pi

            while joint_angle < -math.pi:
                joint_angle += 2 * math.pi

            joint_angles.append(joint_angle)

        return joint_angles

    def plot(self):
        self.fig = plt.figure()
        self.ax = Axes3D(self.fig)

        x_list = []
        y_list = []
        z_list = []

        trans = np.identity(4)

        x_list.append(trans[0, 3])
        y_list.append(trans[1, 3])
        z_list.append(trans[2, 3])
        for i in range(len(self.link_list)):
            trans = np.dot(trans, self.link_list[i].transformation_matrix())
            x_list.append(trans[0, 3])
            y_list.append(trans[1, 3])
            z_list.append(trans[2, 3])

        self.ax.plot(x_list, y_list, z_list, "o-", color="#00aa00", ms=4,
                     mew=0.5)
        self.ax.plot([0], [0], [0], "o")

        plt.show()

def send_angles_sim(J, marker_pos):
    mycobot_sim = NLinkArm([[0., math.pi / 2, 0, 0.140*1000],
                        [0., 0., -0.1104*1000, 0.],
                        [0., 0., -0.096*1000, 0.],
                        [0., math.pi / 2, 0., 0.06639*1000],
                        [0., -math.pi / 2, 0., 0.07318*1000],
                        [0., 0., 0., 0.0436*1000]])

    mycobot_sim.send_angles(
        mycobot_sim.convert_joint_angles_sim_to_mycobot
        ([-math.radians(J[0]), -math.radians(J[1]), math.radians(J[2]), -math.radians(J[3]), -math.radians(J[4]), -math.radians(J[5])]))
    mycobot_sim.forward_kinematics(plot=True, marker_pos=marker_pos)


if __name__ == "__main__":

    J = [-26.76, -65.65, -97.57, 73.22, 0.0, -26.76]
    marker_pos = [150,-150,50]

    send_angles_sim(J=J, marker_pos=marker_pos)