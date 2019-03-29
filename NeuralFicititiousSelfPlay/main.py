# -*- coding:utf-8 -*-
import sys, logging
import tensorflow as tf
from NeuralFicititiousSelfPlay.Leduc.newenv import Env
from NeuralFicititiousSelfPlay.agent.agent import Agent
import numpy as np
import argparse
import configparser
import random
import logging
import time
import matplotlib.pyplot as plt
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# log = logging.getLogger('')


# Configuration
Config = configparser.ConfigParser()
Config.read("./config.ini")


def train(env, player1, player2):
    eta = float(Config.get('Agent', 'Eta'))
    players = [player1, player2]
    dealer = random.randint(0, 1)
    plotter = []

    for i in range(int(Config.get('Common', 'Episodes'))):
        if dealer == 0: # 每局开始互换大小盲注的位置
            dealer = 1
        else:
            dealer = 0  # 表示小盲注的位置
        # Set dealer, reset env and pass dealer to it
        env.reset(dealer)

        lhand = 1 if dealer == 0 else 0 # dealer ;小盲注 lhand :大盲注
        policy = np.array(['', ''])
        # Set policies sigma  设置策略类型，双方玩家以概率eta执行最优反应策略
        if random.random() > eta:
            policy[dealer] = 'a'
        else:
            policy[dealer] = 'b'

        if random.random() > eta:
            policy[lhand] = 'a'
        else:
            policy[lhand] = 'b'

        # Observe initial state for dealer
        d_s = env.get_state(dealer)[3]

        terminated = False
        first_round = True
        d_t = False
        l_t = False

        while not terminated:
            actual_round = env.round_index()
            if first_round and not d_t:  # 游戏开始小盲注首先决策
                d_t = players[dealer].play(policy[dealer], dealer, s2=d_s, batch=i) # 表示小盲注玩家是否结束游戏
                first_round = False
            elif not first_round and not d_t:
                d_t = players[dealer].play(policy[dealer], dealer,batch=i)

            if not l_t:
                l_t = players[lhand].play(policy[lhand], lhand,batch=i)

            if actual_round == env.round_index() and not d_t:
                d_t = players[dealer].play(policy[dealer], dealer,batch=i)

            if d_t and l_t:
                terminated = True

        if i > 150 and i % 100 == 0:
            print("================ Stats {0}th ==================".format(i))
            for player in players:
                player.sampled_actions()
            ex = players[0].average_payoff_br() + players[1].average_payoff_br()
            print("Exploitability: {}".format(ex))
            print("players 0 Exploitability: {}".format(players[0].average_payoff_br()))
            print("players 1 Exploitability: {}".format(players[1].average_payoff_br()))
            plotter.append(ex)

    plt.plot(plotter)
    plt.show()
    time.sleep(60)


def main(args):

    with tf.Session() as sess:
        # initialize env
        env = Env()
        np.random.seed(int(Config.get('Utils', 'Seed')))
        tf.set_random_seed(int(Config.get('Utils', 'Seed')))

        # initialize dimensions:
        state_dim = env.observation_space()
        action_dim = env.action_space()

        # initialize players
        player1 = Agent(sess, state_dim, action_dim, 'Player0', env)
        player2 = Agent(sess, state_dim, action_dim, 'Player1', env)

        # initialize tensorflow variables
        sess.run(tf.global_variables_initializer())

        train(env, player1, player2)


if __name__ == '__main__':

    start_time = time.time()

    print("NFSP by David Joos")
    parser = argparse.ArgumentParser(description='Provide arguments for NFSP agent.')

    parser.add_argument('--human', help='starts testfunc function instead of main', action='store_true')

    args = vars(parser.parse_args())

    main(args)

    print("============= run time =========")
    print(time.time() - start_time)