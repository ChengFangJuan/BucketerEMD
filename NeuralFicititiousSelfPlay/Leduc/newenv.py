# -*- coding:utf-8 -*-
from __future__ import print_function
from NeuralFicititiousSelfPlay.Leduc.deck import Deck
import numpy as np
import configparser
import time

class Env():

    def __init__(self):

        # Init config
        self.config = configparser.ConfigParser()
        self.config.read("./config.ini")

        # Init config variables
        self.player_count = int(self.config.get('Environment', 'Playercount'))  # 2
        self.decksize = int(self.config.get('Environment', 'Decksize')) # 6
        self.max_rounds = int(self.config.get('Environment', 'MaxRounds')) # 2
        self.suits = int(self.config.get('Environment', 'Suits')) # 2
        self.max_raises = int(self.config.get('Environment', 'MaxRaises')) # 3
        self._action_space = int(self.config.get('Environment', 'ActionSpace')) # 2
        self.total_action_space = int(self.config.get('Environment', 'TotalActionSpace')) # 3

        # Init deck
        self.deck = Deck(self.decksize)

        # Init cards vector
        self.cards = []

        # Who is dealer? Important for blinds.
        self.dealer = 0

        # Init game variables
        self.specific_cards = np.zeros((self.player_count, self.max_rounds, int((self.decksize / self.suits)))) # [2,2,3]
        self.round = 0
        self.terminated = False
        self.raises = []
        self.public_card_index = 0
        self.overall_raises = []
        self.reward = np.zeros(self.player_count)
        self.round_raises = 0
        self.last_action = []

        self.actions_done = []
        self.reward_made_index = 0

        # Init specific state
        self.history = np.zeros((self.player_count, self.max_rounds, self.max_raises, self._action_space)) # [2,2,3,2]

        self.s = np.array([[np.zeros(30)], [np.zeros(30)]])
        # DEBUG
        # self.test = 0

    # @property
    # current round
    def round_index(self):
        return self.round

    # @property
    def action_space(self):
        a = np.zeros(self.total_action_space)
        return a.shape

    # @property
    def observation_space(self):
        o = self.history.flatten()
        c = self.specific_cards[0].flatten()
        s = np.concatenate((o, c), axis=0)
        s = np.zeros((1, len(s)))
        return s.shape

    def reset(self, dealer):
        self.dealer = dealer
        n = 1 if dealer == 0 else 0
        # Dealer has to set small blind, n_dealer has to set big blind
        self.overall_raises = np.zeros(self.player_count)
        self.overall_raises[dealer] += 0.5   # 本局游戏累计的押注额
        self.overall_raises[n] += 1

        # Re-init deck as Object of type deck
        self.deck = Deck(self.decksize)
        self.deck.shuffle()

        self.s = np.array([[np.zeros(30)], [np.zeros(30)]]) # 执行动作之前的状态

        self.reward_made_index = 0

        # Reset history to empty
        self.history = np.zeros((self.player_count, self.max_rounds, self.max_raises, self._action_space))

        self.round = 0
        self.terminated = False
        self.raises = np.zeros(self.player_count) # 本回合双方加注动作的次数
        self.public_card_index = 0
        self.reward = np.zeros(self.player_count) # 本局游戏双方的输赢
        self.round_raises = 0 # 本回合双方执行的除弃牌以外的所有动作数
        self.last_action = np.zeros((self.player_count, self.total_action_space)) # [2,3]

        self.actions_done = [] # 本回合双方执行的所有动作

        # Init specific cards
        self.specific_cards = np.zeros((self.player_count, self.max_rounds, int((self.decksize / self.suits))))

        # Init players specific state
        for k in range(self.player_count):
            card_index = self.deck.pick_up().rank
            # Because 6 cards with 3 duplicates we just need 3 entrys in cards vector
            # Each possible rank is represented by one vector object
            # Set cards vector entry to 1 where the picked up card matches
            self.specific_cards[k][self.round][card_index] = 1

    def get_state(self, p_index):
        cards = self.specific_cards[p_index]
        state = np.concatenate((self.history.flatten(), self.specific_cards[p_index].flatten()))
        action = self.last_action[p_index]

        # Reshape to (1, 1, 3)
        state = np.reshape(state, (1, 1, 30))
        action = np.reshape(action, (1, 1, 3))

        if self.terminated:
            return self.s[p_index], action, self.reward[p_index], state, self.terminated
        else:
            # Return zero as reward because there is no
            return self.s[p_index], action, 0, state, self.terminated # state包括历史动作和可见牌的信息

    def do_action(self, action, p_index):

        # Get action with highest value 执行最大动作值的动作
        # print("THE ACTION: {}".format(action))
        action_value = np.argmax(action)
        self.last_action[p_index] = action

        # If player has raised in this round before - action_value is set to
        # call - 0 to 2 raises are allowed. Maximum one raise per player.
        # AND prevent: Call, Raise, Raise: 限制玩家的动作，本回合中玩家只可以加注一次，不可以反复加注
        if self.raises[p_index] > 0 and action_value == 2:
            action_value = 1
        if len(self.actions_done) == 2 and self.actions_done[0] == 'Call' and self.actions_done[1] == 'Raise' \
                and action_value == 2:
            action_value = 1

        # Execute actions:
        # Fold:
        if action_value == 0:
            self.actions_done.append('Fold')
            return True

        # Check, call
        elif action_value == 1:
            self.history[p_index][self.round][self.round_raises][0] = 1
            self.round_raises += 1 # 本回合双方玩家总共执行动作的次数，除去弃牌的动作，最大的动作数是3
            if len(self.actions_done) > 0 and self.actions_done[len(self.actions_done) - 1] == "Raise":
                self.overall_raises[p_index] += 1
            if self.round == 0 and len(self.actions_done) == 0: # 表示盲注执行动作
                # It's the Dealer, he has to double his small blind
                self.overall_raises[p_index] += 0.5
            self.actions_done.append('Call')
            return False

        # Raise
        elif action_value == 2:
            self.history[p_index][self.round][self.round_raises][1] = 1
            self.raises[p_index] += 1
            if len(self.actions_done) > 0 and self.actions_done[len(self.actions_done) - 1] == "Raise":
                self.overall_raises[p_index] += 2
            else:
                self.overall_raises[p_index] += 1
            self.round_raises += 1
            if self.round == 0 and len(self.actions_done) == 0:
                # It's the Dealer, he has to double his small blind
                self.overall_raises[p_index] += 0.5
            self.actions_done.append('Raise')
            return False

    def game_or_round_has_terminated(self): # 判断是否进入新的回合
        if len(self.actions_done) == 2:
            if self.actions_done[0] == 'Call' and self.actions_done[1] == 'Call' \
                    or self.actions_done[0] == 'Raise' and self.actions_done[1] == 'Call':
                return True
        elif len(self.actions_done) == 3:
            if self.actions_done[0] == 'Call' and self.actions_done[1] == 'Raise' and self.actions_done[2] == 'Call' \
                    or self.actions_done[0] == 'Raise' and self.actions_done[1] == 'Raise' and self.actions_done[2] == 'Call':
                return True
        else:
            return False

    def step(self, action, p_index):
        """
        :param action:
        :param p_index:
        :return:
        """

        cards = self.specific_cards[p_index]
        state = np.concatenate((self.history.flatten(), self.specific_cards[p_index].flatten()))
        self.s[p_index][0][:] = state

        if not self.terminated:
            # Deconstruct raises, calls, round etc
            o_index = 1 if p_index == 0 else 0  # TODO: make it dynamic for more than 2 players!

            # Do action
            self.terminated = self.do_action(action, p_index)

            if not self.terminated and self.game_or_round_has_terminated():
                if self.round == 1:
                    # Game has terminated
                    self.terminated = True
                elif self.round == 0:
                    # Update card vector of next round with private card from round_k-1
                    self.specific_cards[p_index][(self.round + 1)] = self.specific_cards[p_index][self.round]
                    self.specific_cards[o_index][(self.round + 1)] = self.specific_cards[o_index][self.round]

                    # Update card vector for next round with revealed public card
                    self.public_card_index = self.deck.pick_up().rank
                    self.specific_cards[p_index][(self.round + 1)][self.public_card_index] = 1
                    self.specific_cards[o_index][(self.round + 1)][self.public_card_index] = 1
                    # print("This the new state:")
                    # print("Player{} - {}".format(p_index, self.specific_cards[p_index][1]))
                    # print("Player{} - {}".format(o_index, self.specific_cards[o_index][1]))

                    # Determine reward from first round
                    # if p_index == self.dealer:
                    #     self.reward[p_index] = self.overall_raises
                    #
                    # self.reward[o_index] = np.sum(self.overall_raises)
                    self.round = 1

                    # Set raises and calls to zero - in new round nothing happened
                    # so far
                    self.raises = np.zeros(2)
                    self.round_raises = 0
                    # Print actions done in round:
                    # print("Player{} has finised".format(p_index))
                    # print("Actions done: {}".format(self.actions_done))
                    self.actions_done = []

                else:
                    print("Round not specified.")
                if abs(self.reward[p_index]) - abs(self.reward[o_index]) != 0:
                    print("IF p-index: {}, o_index: {} ".format(self.reward[p_index], self.reward[o_index]))

            # Determine rewards if terminated
            if self.terminated:
                # Player has folded: Reward is at least zero
                if np.argmax(action) == 0:

                    self.reward[p_index] = self.overall_raises[p_index] * (-1)
                    self.reward[o_index] = self.overall_raises[p_index]

                    if abs(self.reward[p_index]) - abs(self.reward[o_index]) != 0:
                        print("p-index: {}, o_index: {}".format(self.reward[p_index], self.reward[o_index]))

                # No one has folded, check winner by card
                elif np.argmax(action) > 0:
                    # Deconstruct cards
                    p_cards = self.specific_cards[p_index][self.round]
                    o_cards = self.specific_cards[o_index][self.round]

                    # Compute total reward
                    self.reward[p_index] = self.overall_raises[o_index]
                    self.reward[o_index] = self.overall_raises[p_index]

                    # Check if one player has same card as public card
                    # If just one index has value 1, the player has same rank
                    # as public card.
                    if np.count_nonzero(p_cards) == 1:
                        # Player wins
                        self.reward[o_index] *= -1
                    elif np.count_nonzero(o_cards) == 1:
                        # Opponent wins
                        self.reward[p_index] *= -1
                    else:
                        # No player has match with public card, remove public card
                        # if round == 1:
                        if self.round == 1:
                            p_cards[self.public_card_index] = 0
                            o_cards[self.public_card_index] = 0
                        if np.argmax(p_cards) < np.argmax(o_cards):
                            # Player wins
                            self.reward[o_index] *= -1
                        elif np.argmax(p_cards) > np.argmax(o_cards):
                            # Opponent wins
                            self.reward[p_index] *= -1
                        elif np.argmax(p_cards) == np.argmax(o_cards):
                            # Draw
                            self.reward = np.zeros(2)
                        else:
                            print("SOMETHING ELSE HAPPENED"*4)
                        if self.round == 1:
                            p_cards[self.public_card_index] = 1
                            o_cards[self.public_card_index] = 1

                if self.reward[p_index] + self.reward[o_index] != 0:
                    print("FUCK MAN")
        else:
            # pass
            print("Player{} tried to step while self.terminated is {}".format(p_index, self.terminated))
            # time.sleep(5)