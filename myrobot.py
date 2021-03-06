#!/usr/bin/env python3
"""
    robot class
"""

import numpy as np


class Robot(object):
    """
        class to take care of basic robot operations
    """
    MAP = np.array([[0.0, 0.0], [1.0, 1.0]])
    MAP_SIZE = 2
    WORLD_SIZE = 100
    def __init__(self, pose):
        """ constructor

            :pose: array/list of pose [x, y, phi]

        """
        self.pose = [float(value) for value in pose]
        self.motion_noise = [0.0, 0.0]
        self.sense_noise = 0.0
        self.__turn_noise = 0.0
        self.__forward_noise = 0.0
        self.__sense_noise = 0.0
        self.__motion_cmd = [0.0, 0.0]


    def set_noise(self, turn_noise, forward_noise, sense_noise):
        """ set the robot noise

            :turn_noise: uncertainity in rotation
            :forward_noise: uncertainity in translation
            :sense_nose: uncertainity in measurement

        """
        self.__turn_noise, self.__forward_noise = turn_noise, forward_noise
        self.__sense_noise = sense_noise

    def set_motion_cmd(self, turn, forward):
        """

            :turn: set the robot motion
            :forward: translation in float

        """
        self.__motion_cmd = [float(turn), float(forward)]


    def motion_update(self, x, y, phi):
        """function to get upated robot pose
        """
        phi += self.__motion_cmd[0] + np.random.normal(size=len(phi)) * self.__turn_noise
        phi %= np.pi * 2
        delta = self.__motion_cmd[1] + np.random.normal(size=len(x)) * self.__forward_noise
        x += np.cos(phi) * delta
        y += np.sin(phi) * delta
        return [x, y, phi]

    def move(self, turn, forward):
        """ function to move robot """
        self.set_motion_cmd(float(turn), float(forward))
        x, y, phi = self.pose
        phi += self.__motion_cmd[0] + np.random.normal() * self.__turn_noise
        phi %= np.pi * 2
        delta = self.__motion_cmd[1] + np.random.normal() * self.__forward_noise
        x += np.cos(phi) * delta #  % Robot.WORLD_SIZE
        y += np.sin(phi) * delta #  % Robot.WORLD_SIZE
        self.pose = [x, y, phi]

    @classmethod
    def __set_map__(cls, landmarks):
        Robot.MAP = np.array(landmarks, dtype=np.float).reshape(-1, 2)
        Robot.MAP_SIZE = len(landmarks)

    def sense(self):
        """sensor measurement"""
        cur_pose = np.array(self.pose[:2], dtype=np.float).reshape(1, 2)
        diff = Robot.MAP - cur_pose
#         print(diff.shape,cur_pose.shape,Robot.MAP_SIZE)
        return np.hypot(diff[:, 0], diff[:, 1]) + np.random.normal(size=Robot.MAP_SIZE) * self.sense_noise

    def predict(self, state, cmd, noise, delta_t):
        """method to perform EKF prediction

        :state: Current state of the robot
        :cmd: motion command
        :returns: [next_state, jac wrt x]

        """

        x, y, phi, trans = state
        turn, forward = cmd
        turn_noise, forward_noise = noise
        phi += turn + turn_noise
        trans = forward +  forward_noise
        phi = (phi + np.pi) % (np.pi * 2) - np.pi
        x += np.cos(phi) * trans
        y += np.sin(phi) * trans
        next_state = np.array([x, y, phi, trans])

        f_wrt_x = np.array([[1, 0, -np.sin(phi) * trans, 0],
                            [0, 1, np.cos(phi) * trans, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
        f_wrt_n = np.array([[0, 0],
                            [0, 0],
                            [1, 0],
                            [0, 1]])
        return [next_state, f_wrt_x, f_wrt_n]
        
# -----------jsola model--------------# 
        # px, py, vx, vy = state
        # ax, ay = cmd
        # nx, ny = noise
        # px += vx * delta_t
        # py += vy * delta_t
        # vx += ax * delta_t + nx
        # vy += ay * delta_t + ny

        # next_state = np.array([px, py, vx, vy])

        # f_wrt_x = np.array([[1, 0, delta_t, 0],
        #                     [0, 1, 0, delta_t],
        #                     [0, 0, 1, 0],
        #                     [0, 0, 0, 1]])

        # f_wrt_n = np.array([[0, 0],
        #                     [0, 0],
        #                     [1, 0],
        #                     [0, 1]])

        # return [next_state, f_wrt_x, f_wrt_n]


    def sense_linear(self, state):
        """method to sense and linearise
        :state: state of the robot
        :returns: [range, Jac of H wrt to x]"""
        # cur_pose = np.array(state[:2], dtype=np.float).reshape(1, 2)
        # diff = Robot.MAP - cur_pose
        # ranges = np.hypot(diff[:, 0], diff[:, 1]) + noise
        y = np.array([np.hypot(state[0], state[1]), np.arctan2(state[1], state[2])])
        # h_wrt_x = np.array([state[0] / y[0],  state[1] /y[0], np.zeros(Robot.MAP_SIZE), np.zeros(Robot.MAP_SIZE)]).T
        px, py, _, _ = state
        t = (py/px) ** 2 + 1
        h_wrt_x = np.array([[px / y[0], py /y[0], 0, 0],
                            [-py / ((px **2) * t), 1/(px * t), 0, 0]])
        return [y, h_wrt_x]

    def obs(self, state):
        """TODO: Docstring for obs.

        :state: robot state
        :returns: [measurement_estimate, measurement_jacobian]

        """
        pass

    def advance(self, state, cmd, delta_t, noise):
        """method to advance the robot with given commands

        :state: state mean
        :cmd: input [linear_vel, ang_vel]
        :delta_t: time interval
        :noise: additive noise
        :returns: [next_state, jac_wrt_x]

        """
