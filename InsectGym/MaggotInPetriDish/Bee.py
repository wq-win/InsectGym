import random
import sys
from contextlib import closing
from io import StringIO
from gym import utils
from gym.envs.toy_text import discrete
import numpy as np


MAP = [
    "    +-----+",
    "bee | : : |",
    "food| : : |",
    "    +-----+",
]


class BeeFoodEnv(discrete.DiscreteEnv):
    def __init__(self, num_locations=3):
        self.num_locations = num_locations
        self.reward_options = (0, 1)
        # self.bee_locations = self.num_locations
        # self.food_loactions = self.num_locations
        # TODO: observation 是bee的state * food的state 还是只有bee的location？
        # num_states = self.bee_locations * self.food_loactions
        num_states = self.num_locations * self.num_locations
        
        initial_state_distrib = np.zeros(num_states)
        initial_state_distrib[0] = 1  # TODO:可以让0，1，2三个状态平均概率随机 [0:3]=1
        initial_state_distrib /= initial_state_distrib.sum()

        num_actions = 3  # 0:拽 1:休息 2:右移
        
        P = {
            state: {action: [] for action in range(num_actions)}
            for state in range(num_states)
        }
        # P[s][a] == [(probability, nextstate, reward, done), ...]
        
        for state in range(num_states):
            for action in range(num_actions):
                done = False
                
                if (state == 7 and action == 2) or (state == 5 and action == 0) or state == 8:
                    reward = self.reward_options[1]
                else:
                    reward = self.reward_options[0]
                
                if reward == self.reward_options[1]:
                    done = True
                
                prob = 1
                if action == 0:
                    if state in (0, 3, 4):  # 拽食物更困难
                        prob = .6
                    next_state = state + self.num_locations
                    
                    if state in (6, 7, 8):  # 若food在最右边，继续拽，状态不变
                        next_state = state  
                elif action == 1:
                    next_state = state
                    # prob = 1
                else:
                    next_state = state + 1
                    # prob = 1
                    prob = .88  # 一定概率移动失败
                    if state in (2, 5, 8):  # 若bee在最右边，继续右移，状态不变
                        next_state = state
                                
                P[state][action].append((prob, next_state, reward, done))
                if prob != 1:
                    P[state][action].append((1-prob, state, reward,done))  # 动作执行失败，状态不变

        for key, value in P.items():
            print(key,value)      
        # print(P[0][0])
        self.mapInit()
        discrete.DiscreteEnv.__init__(
            self, num_states, num_actions, P, initial_state_distrib
        )
    
    def mapInit(self):
        self.desc = np.asarray(MAP, dtype="c")
        self.layer_name_length = 3
        # first_letter = 'B'
        # second_letter = 'F'
        # self.desc[1, self.layer_name_length + 2] = first_letter
        # self.desc[2, self.layer_name_length + 2] = second_letter
    
    def render(self, mode="human"):
        outfile = StringIO() if mode == "ansi" else sys.stdout
        out = self.desc.copy().tolist()    
        out = [[c.decode("utf-8") for c in line] for line in out]
        bee_location = self.s % self.num_locations
        food_location = self.s // self.num_locations
        out[1][self.layer_name_length + (bee_location + 1) * 2] = utils.colorize('B', "yellow", highlight=True)
        out[2][self.layer_name_length + (food_location + 1) * 2] = utils.colorize('F', "green", highlight=True)
        outfile.write("\n".join(["".join(row) for row in out]) + "\n")
        # No need to return anything for human
        if mode != "human":
            with closing(outfile):
                return outfile.getvalue()
            
            
if __name__ == "__main__":
    env = BeeFoodEnv()
    obs = env.reset()
    while True:
        action = env.action_space.sample()
    
        obs, reward, done, info = env.step(action)

        print('action:%d, state:%d, reward:%d, done:%s, info:%s' % (action, obs, reward, done, info))
    
        env.render()
    
        if done:
            print('done')
            break
    
    env.close()