# -*- coding:utf-8 -*-

from BucketerEMD.judging import judging
import random
import numpy as np
from pyemd import emd
import copy
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
from scipy.special import comb, perm
from itertools import combinations,permutations
import math


class CLUSTER_RESULT():

    def __init__(self, street = None, board_sample_count =100, turn_sample_count = 7, river_sample_count = 6,
                 opponent_sample_count = 100, comb_flag = False):

        self.card_to_string = CARD_TO_STRING()
        self.cards = self.get_all_cards()
        self.street = street
        self.sample_state_count = None
        self.cluster_result_file = None
        self.card_to_cluster_dict = dict()
        self.board_sample_count = board_sample_count
        self.turn_sample_count = turn_sample_count
        self.river_sample_count = river_sample_count
        self.opponent_sample_count = opponent_sample_count
        self.comb_flag = comb_flag

    # 生成所有牌的组合
    def get_all_cards(self):
        cards = []
        card = self.card_to_string.rank_table[:settings.rank_count]
        flower = self.card_to_string.suit_table[:settings.suit_count]
        # 生成所有牌
        for i in card:
            for j in flower:
                cards.append(i + j)
        return cards

    def string_to_list(self,card):
        assert len(card) % 2 == 0, "the number of string card is wrong"
        card_count = len(card) // 2
        card_list = []
        iter_count = 0
        card_string_start = 0
        while iter_count < card_count:
            card_list.append(card[card_string_start:(card_string_start+2)])
            card_string_start +=2
            iter_count += 1
        assert len(card_list) == card_count, 'the number of card is wrong'
        return card_list

    def _computer_river_card_win(self, hand, board):
        out_win_rate = 0
        count = 0
        used_card_list = hand + board
        available_card = copy.deepcopy(self.cards)
        hand_card = self.list_to_string(hand)
        board_card = self.list_to_string(board)

        for card in used_card_list:
            available_card.remove(card)

        for i in range(self.opponent_sample_count):
            print('{0} th iter'.format(count))
            opponent_card = random.sample(available_card,2)
            opponent = opponent_card[0] + opponent_card[1]
            if judging(hand_card, opponent, board_card) == 0:
                out_win_rate += 1
            count += 1
        out_win_rate = out_win_rate / count
        out_win_rate = round(out_win_rate, 2)
        return out_win_rate

    def _computer_river_card_win_comb(self, hand, board, state):
        out_win_rate = 0
        available_card = copy.deepcopy(self.cards)
        count = 0

        for card in state:
            available_card.remove(card)

        opponent_cards = list(combinations(available_card,2))
        for card in opponent_cards:
            # print('{0} th iter'.format(count))
            opponent_card = list(card)
            opponent = opponent_card[0] + opponent_card[1]
            if judging(hand, opponent, board) == 0 or judging(hand, opponent, board) == 2:
                out_win_rate += 1
            count += 1
        out_win_rate = out_win_rate / count
        out_win_rate = round(out_win_rate, 2)
        return out_win_rate

    def _computer_turn_card_win(self, hand, board):

        win_rate = 0
        count = 0
        used_card_list = hand + board
        available_card = copy.deepcopy(self.cards)
        hand_card = self.list_to_string(hand)
        for card in used_card_list:
            available_card.remove(card)

        for i in range(self.river_sample_count):
            river_board = copy.deepcopy(board)
            river_card = random.sample(available_card, 1)
            river_board.append(river_card[0])
            opponent_available_card = copy.deepcopy(available_card)
            opponent_available_card.remove(river_card[0])
            board_card = self.list_to_string(river_board)
            assert len(board_card) // 2 == 5, "the number of the river board is not 5"
            for _ in range(self.opponent_sample_count):
                opponent_card = random.sample(opponent_available_card, 2)
                opponent = opponent_card[0] + opponent_card[1]
                if judging(hand_card, opponent, board_card) == 0:
                    win_rate += 1
                count += 1
        win_rate = win_rate / count
        win_rate = round(win_rate, 2)
        return win_rate

    def _computer_turn_card_win_comb(self, hand, board, state):

        win_rate = 0
        count = 0
        available_card = copy.deepcopy(self.cards)
        for card in state:
            available_card.remove(card)

        for river_card in available_card:
            river_board = board + river_card
            opponent_available_card = copy.deepcopy(available_card)
            opponent_available_card.remove(river_card)
            assert len(river_board) // 2 == 5, "the number of the river board is not 5"
            opponent_cards = list(combinations(opponent_available_card,2))
            for card in opponent_cards:
                opponent_card = list(card)
                opponent = opponent_card[0] + opponent_card[1]
                if judging(hand, opponent, river_board) == 0 or judging(hand, opponent, river_board) == 2:
                    win_rate += 1
                count += 1
        win_rate = round(win_rate / count, 2)
        return win_rate

    def _computer_flop_card_win(self, hand, board):

        win_rate = 0
        count = 0
        used_card_list = hand + board
        available_card = copy.deepcopy(self.cards)
        hand_card = self.list_to_string(hand)

        for card in used_card_list:
            available_card.remove(card)
        for i in range(self.turn_sample_count):
            turn_board = copy.deepcopy(board)
            turn_card = random.sample(available_card,1)
            turn_board.append(turn_card[0])
            river_available_card = copy.deepcopy(available_card)
            river_available_card.remove(turn_card[0])
            assert len(river_available_card) == 6, "The number of river available card is not 6"
            assert len(turn_board) == 4, "The number of turn board is not 4"
            for j in range(self.river_sample_count):
                river_board = copy.deepcopy(turn_board)
                river_card = random.sample(river_available_card, 1)
                river_board.append(river_card[0])
                opponent_available_card = copy.deepcopy(river_available_card)
                opponent_available_card.remove(river_card[0])
                board_card = self.list_to_string(river_board)
                assert len(opponent_available_card) == 5, "The number of opponent available card is not 5"
                assert len(board_card) // 2 == 5, "the number of the river board is not 5"
                for _ in range(self.opponent_sample_count):
                    opponent_card = random.sample(opponent_available_card, 2)
                    opponent = opponent_card[0] + opponent_card[1]
                    if judging(hand_card, opponent, board_card) == 0:
                        win_rate += 1
                    count += 1
        win_rate = round(win_rate / count, 2)
        return win_rate

    def _computer_flop_card_win_comb(self, hand, board, state):

        win_rate = 0
        count = 0
        available_card = copy.deepcopy(self.cards)
        for card in state:
            available_card.remove(card)

        for turn_card in available_card:
            turn_board = board + turn_card
            river_available_card = copy.deepcopy(available_card)
            river_available_card.remove(turn_card)
            assert len(river_available_card) == 6, "The number of river available card is not 6"
            assert len(turn_board) // 2 == 4, "The number of turn board is not 4"
            for river_card in river_available_card:
                river_board = turn_board + river_card
                opponent_available_card = copy.deepcopy(river_available_card)
                opponent_available_card.remove(river_card)
                assert len(opponent_available_card) == 5, "The number of opponent available card is not 5"
                assert len(river_board) // 2 == 5, "the number of the river board is not 5"
                opponent_cards = list(combinations(opponent_available_card, 2))
                for card in opponent_cards:
                    opponent_card = list(card)
                    opponent = opponent_card[0] + opponent_card[1]
                    if judging(hand, opponent, river_board) == 0 or judging(hand, opponent, river_board) == 2:
                        win_rate += 1
                    count += 1
        win_rate = round(win_rate / count, 2)
        return win_rate

    def _computer_pre_flop_card_win(self, hand):

        win_rate = 0
        count = 0
        used_card_list = hand
        available_card = copy.deepcopy(self.cards)
        hand_card = self.list_to_string(hand)
        for card in used_card_list:
            available_card.remove(card)

        for k in range(self.board_sample_count):
            board = random.sample(available_card, 3)
            turn_available_card = copy.deepcopy(available_card)
            for board_card in board:
                turn_available_card.remove(board_card)

            for i in range(self.turn_sample_count):
                turn_board = copy.deepcopy(board)
                turn_card = random.sample(turn_available_card,1)
                turn_board.append(turn_card[0])
                river_available_card = copy.deepcopy(turn_available_card)
                river_available_card.remove(turn_card[0])
                assert len(river_available_card) == 6, "The number of river available card is not 6"
                assert len(turn_board) == 4, "The number of turn board is not 4"
                for j in range(self.river_sample_count):
                    river_board = copy.deepcopy(turn_board)
                    river_card = random.sample(river_available_card, 1)
                    river_board.append(river_card[0])
                    opponent_available_card = copy.deepcopy(river_available_card)
                    opponent_available_card.remove(river_card[0])
                    board_card = self.list_to_string(river_board)
                    assert len(opponent_available_card) == 5, "The number of opponent available card is not 5"
                    assert len(board_card) // 2 == 5, "the number of the river board is not 5"
                    for _ in range(self.opponent_sample_count):
                        opponent_card = random.sample(opponent_available_card, 2)
                        opponent = opponent_card[0] + opponent_card[1]
                        if judging(hand_card, opponent, board_card) == 0:
                            win_rate += 1
                        count += 1
        win_rate = round(win_rate / count, 2)
        return win_rate

    def _computer_pre_flop_card_win_comb(self, hand, state):

        win_rate = 0
        count = 0
        available_card = copy.deepcopy(self.cards)
        for card in state:
            available_card.remove(card)

        board_cards = list(combinations(available_card, 3))
        print('board count:', comb(10,3))
        for board_card in board_cards:
            board_card = list(board_card)
            turn_available_card = copy.deepcopy(available_card)
            for i in board_card:
                turn_available_card.remove(i)
            board = board_card[0] + board_card[1] + board_card[2]

            for turn_card in turn_available_card:
                turn_board = board + turn_card
                river_available_card = copy.deepcopy(turn_available_card)
                river_available_card.remove(turn_card)
                assert len(river_available_card) == 6, "The number of river available card is not 6"
                assert len(turn_board) // 2 == 4, "The number of turn board is not 4"
                for river_card in river_available_card:
                    river_board = turn_board + river_card
                    opponent_available_card = copy.deepcopy(river_available_card)
                    opponent_available_card.remove(river_card)
                    assert len(opponent_available_card) == 5, "The number of opponent available card is not 5"
                    assert len(river_board) // 2 == 5, "the number of the river board is not 5"
                    opponent_cards = list(combinations(opponent_available_card, 2))
                    for card in opponent_cards:
                        opponent_card = list(card)
                        opponent = opponent_card[0] + opponent_card[1]
                        if judging(hand, opponent, river_board) == 0 or judging(hand, opponent, river_board) == 2:
                            win_rate += 1
                        count += 1
        win_rate = round(win_rate / count, 2)
        return win_rate

    def list_to_string(self,list1):
        string1 = ''
        for i in range(len(list1)):
            string1 = string1 + str(list1[i])
        return string1

    def computer_win_result(self):

        if self.street == "river":
            file_name = "river_win_rate.txt"
            self.cluster_result_file = open(file_name, "w")
            self.sample_state_count = 7
        elif self.street == "turn":
            file_name = "turn_win_rate.txt"
            self.cluster_result_file = open(file_name, "w")
            self.sample_state_count = 6
        elif self.street == "flop":
            file_name = "flop_win_rate.txt"
            self.cluster_result_file = open(file_name, "w")
            self.sample_state_count = 5
        elif self.street == "preflop":
            file_name = "preflop_win_rate.txt"
            self.cluster_result_file = open(file_name, "w")
            self.sample_state_count = 2
        else:
            pass

        all_state = list(combinations(self.cards, self.sample_state_count))
        state_count = 0
        for state in all_state:
            state = list(state)
            print('state {0}:'.format(state_count), self.list_to_string(state))
            possible_hand_comb = list(combinations(state, settings.hold_card_count))
            hand_count = 0
            for hand in possible_hand_comb:
                hand = list(hand)
                print("--- {0} th hand".format(hand_count), self.list_to_string(hand))
                hand_card = hand[0] + hand[1]
                board_card = ""
                board = []
                if self.street != 'preflop':
                    board = copy.deepcopy(state)
                    for card in hand:
                        board.remove(card)
                    for i in range(len(board)):
                        board_card = board_card + board[i]
                # board_card = board[0] + board[1] + board[2] + board[3] + board[4]

                if self.street == "river":
                    if self.comb_flag:
                        win_rate = self._computer_river_card_win_comb(hand_card,board_card,state)
                    else:
                        win_rate = self._computer_river_card_win(hand,board)
                elif self.street == "turn":
                    if self.comb_flag:
                        win_rate = self._computer_turn_card_win_comb(hand_card,board_card,state)
                    else:
                        win_rate = self._computer_turn_card_win(hand,board)
                elif self.street == "flop":
                    if self.comb_flag:
                        win_rate = self._computer_flop_card_win_comb(hand_card,board_card,state)
                    else:
                        win_rate = self._computer_flop_card_win(hand,board)
                elif self.street == "preflop":
                    if self.comb_flag:
                        win_rate = self._computer_pre_flop_card_win_comb(hand_card, state)
                    else:
                        win_rate = self._computer_pre_flop_card_win(hand)
                else:
                    win_rate = 0

                assert win_rate >= 0 and win_rate <= 1, "The win rate is wrong"

                # print("--- {0} cluster".format(cluster_index))
                hand_card_index = self.card_to_string.string_to_board(hand_card)
                hand_card_index.sort()
                hand_card_index_string = self.list_to_string(hand_card_index)
                if self.street == "preflop":
                    card_index_string = hand_card_index_string
                else:
                    board_card_index = self.card_to_string.string_to_board(board_card)
                    board_card_index.sort()
                    board_card_index_string = self.list_to_string(board_card_index)
                    card_index_string = hand_card_index_string + board_card_index_string
                self.cluster_result_file.write(card_index_string + ":" + str(win_rate) + "\n")
                self.card_to_cluster_dict[card_index_string] = win_rate
                hand_count += 1
            state_count += 1
        assert len(self.card_to_cluster_dict) == comb(12,self.sample_state_count) * comb(self.sample_state_count, \
                    settings.hold_card_count), "the number of possible card combination is wrong"
        print("the result len: {0}".format(len(self.card_to_cluster_dict)))
        print(str(comb(12,self.sample_state_count)) + "*" + str(comb(self.sample_state_count,settings.hold_card_count)))
        self.cluster_result_file.close()


if __name__ == "__main__":

    cluster_result = CLUSTER_RESULT(street="preflop", turn_sample_count=20,river_sample_count=10, opponent_sample_count= 20,
                                    comb_flag = True)
    cluster_result.computer_win_result()