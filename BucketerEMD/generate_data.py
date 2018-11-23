# -*- coding:utf-8 -*-
from __future__ import division
from BucketerEMD.judging import judging
import random
import numpy as np
from pyemd import emd
import copy
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
import math
from itertools import combinations,permutations


class GenerateData():

    def __init__(self, street = None, sample_count = 1000, comb_flag = False, normalize_flag = False):

        self.street = street
        self.sample_count = sample_count
        self.comb_flag = comb_flag
        self.normalize_flag = normalize_flag
        self.card_to_string = CARD_TO_STRING()
        self.cards = self.get_all_cards()
        self.file = open(self.open_file(), 'w')
        self.state_count = self.get_state_count()
        self.get_centroids()


    def get_all_cards(self):
        card = self.card_to_string.rank_table[:settings.rank_count]
        flower = self.card_to_string.suit_table[:settings.suit_count]
        cards = []
        for i in card:
            for j in flower:
                cards.append(i + j)
        return cards

    def open_file(self):
        if self.street == "river":
            file_name = "river_data.csv"
        elif self.street == "turn":
            file_name = "turn_data.csv"
        else:
            file_name = "flop_data.csv"
        return file_name

    def get_state_count(self):
        if self.street == "river":
            state_count = 7
        elif self.street == "turn":
            state_count = 6
        else:
            state_count = 5
        return state_count

    def get_centroids(self):

        if self.street == "turn":
            self.centroids_river = self._get_centroids_street('river')
        elif self.street == 'flop':
            self.centroids_river = self._get_centroids_street('river')
            self.centroids_turn = self._get_centroids_street('turn')

    def _get_centroids_street(self, street_type):
        centroids = []
        file_name = ""
        if street_type == "river":
            file_name = "river_cluster.csv"
            self.cluster_state_count = 1
        elif street_type == "turn":
            file_name = "turn_cluster.csv"
            self.cluster_state_count = settings.river_cluster_count
        elif street_type == "flop":
            file_name = "flop_cluster.csv"
            self.cluster_state_count = settings.turn_cluster_count
        else:
            print("The file name is None")

        with open(file_name) as file:
            for line in file:
                string_line = line.split(",")
                centroid = []
                for i in range(self.cluster_state_count):
                    line_ = float(string_line[i])
                    centroid.append(line_)
                centroids.append(centroid)

        return centroids

    def generate_river_data(self,state):

        out_win_rate = 0
        hand_card = random.sample(state, settings.hold_card_count)
        hand = hand_card[0] + hand_card[1]
        board_available_card = copy.deepcopy(state)
        for card in hand_card:
            board_available_card.remove(card)
        public = board_available_card[0] + board_available_card[1] + board_available_card[2] + board_available_card[3] + board_available_card[4]
        opponent_available_card = copy.deepcopy(self.cards)
        for i in state:
            opponent_available_card.remove(i)
        # print(win_rate)
        for i in range(settings.opponent_sample_count):
            opponent_card = random.sample(opponent_available_card, 2)
            opponent = opponent_card[0] + opponent_card[1]
            if judging(hand, opponent,public) == 0:
                out_win_rate += 1
            #
        return [out_win_rate / settings.opponent_sample_count]

    def generate_river_data_comb(self, hand, public, state):
        out_win_rate = 0
        opponent_available_card = copy.deepcopy(self.cards)
        for i in state:
            opponent_available_card.remove(i)
        # print(win_rate)
        opponent_cards = list(combinations(opponent_available_card,2))
        for card in opponent_cards:
            opponent_card = list(card)
            opponent = opponent_card[0] + opponent_card[1]
            if judging(hand, opponent, public) == 0:
                out_win_rate += 1
            #
        return [out_win_rate / len(opponent_cards)]

    def generate_turn_data(self, state):

        out = [0]* settings.river_cluster_count
        hand_card = random.sample(state, settings.hold_card_count)
        hand = hand_card[0] + hand_card[1]
        board_available_card = copy.deepcopy(state)
        for card in hand_card:
            board_available_card.remove(card)
        public = board_available_card[0] + board_available_card[1] + board_available_card[2] + board_available_card[3]

        turn_available_card = copy.deepcopy(self.cards)
        for card in state:
            turn_available_card.remove(card)
        for i in range(settings.river_sample_count):
            turn_card = random.sample(turn_available_card,1)
            board_card = public + turn_card[0]
            opponent_available_card = copy.deepcopy(turn_available_card)
            opponent_available_card.remove(turn_card[0])

            out_win_rate = 0
            for i in range(settings.opponent_sample_count):
                opponent_card = random.sample(opponent_available_card, 2)
                opponent = opponent_card[0] + opponent_card[1]
                if judging(hand, opponent, board_card) == 0:
                    out_win_rate += 1
            out_win_rate = out_win_rate / settings.opponent_sample_count
            min_distance_index = 0
            min_distance = 10000
            for i in range(settings.river_cluster_count):
                distance = math.pow(self.centroids_river[i][0] - out_win_rate, 2)
                # distance = emd(np.array(win_rate), np.array(centroids[i]), matrix)
                if distance < min_distance:
                    # print(i)
                    min_distance_index = i
                    min_distance = distance
            out[min_distance_index] += 1
        if self.normalize_flag:
            sum_out = sum(out)
            for i in range(len(out)):
                out[i] = out[i] / sum_out
        return out

    def generate_turn_data_comb(self,  hand, public, state):

        out = [0] * settings.river_cluster_count
        turn_available_card = copy.deepcopy(self.cards)
        for card in state:
            turn_available_card.remove(card)

        for card in turn_available_card:
            board_card = public + card
            opponent_available_card = copy.deepcopy(turn_available_card)
            opponent_available_card.remove(card)
            out_win_rate = 0
            opponent_cards = list(combinations(opponent_available_card,2))
            for i in opponent_cards:
                opponent_card = list(i)
                opponent = opponent_card[0] + opponent_card[1]
                if judging(hand, opponent, board_card) == 0:
                    out_win_rate += 1
            out_win_rate = out_win_rate / len(opponent_cards)
            min_distance_index = 0
            min_distance = 10000
            for i in range(settings.river_cluster_count):
                distance = math.pow(self.centroids_river[i][0] - out_win_rate, 2)
                # distance = emd(np.array(win_rate), np.array(centroids[i]), matrix)
                if distance < min_distance:
                    # print(i)
                    min_distance_index = i
                    min_distance = distance
            out[min_distance_index] += 1
        if self.normalize_flag:
            sum_out = sum(out)
            for i in range(len(out)):
                out[i] = out[i] / sum_out
        return out

    def computer_distance_matrix(self, street):

        if street == 'turn':
            matrix = np.zeros([settings.river_cluster_count, settings.river_cluster_count])
            for i in range(settings.river_cluster_count):
                for j in range(settings.river_cluster_count):
                    matrix[i][j] = math.pow(self.centroids_river[i][0]-self.centroids_river[j][0],2)
        elif street == 'flop':
            matrix = np.zeros([settings.turn_cluster_count, settings.turn_cluster_count])
            matrix_turn = np.zeros([settings.river_cluster_count, settings.river_cluster_count])
            for i in range(settings.river_cluster_count):
                for j in range(settings.river_cluster_count):
                    matrix_turn[i][j] = math.pow(self.centroids_river[i][0]-self.centroids_river[j][0],2)
            for i in range(settings.turn_cluster_count):
                for j in range(settings.turn_cluster_count):
                    matrix[i][j] = emd(np.array(self.centroids_turn[i]),np.array(self.centroids_turn[j]), matrix_turn)
        else:
            pass
            matrix = np.array([[0,1/3.0,2/3.0],[1/3.0,0,1/3.0],[2/3.0,1/3.0,0]])
        return matrix

    def generate_flop_data(self, state):

        out = [0.0] * settings.turn_cluster_count
        hand_card = random.sample(state, settings.hold_card_count)
        hand = hand_card[0] + hand_card[1]
        board_available_card = copy.deepcopy(state)
        for card in hand_card:
            board_available_card.remove(card)
        public = board_available_card[0] + board_available_card[1] + board_available_card[2]

        turn_available_card = copy.deepcopy(self.cards)
        for card in state:
            turn_available_card.remove(card)

        for i in range(settings.turn_sample_count):
            turn_card = random.sample(turn_available_card, 1)
            turn_board_card = public + turn_card[0]
            river_available_card = copy.deepcopy(turn_available_card)
            river_available_card.remove(turn_card[0])
            temp_out = [0.0] * settings.river_cluster_count
            for j in range(settings.river_sample_count):
                river_card = random.sample(river_available_card, 1)
                board_card = turn_board_card + river_card[0]
                opponent_available_card = copy.deepcopy(river_available_card)
                opponent_available_card.remove(river_card[0])

                out_win_rate = 0
                for i in range(settings.opponent_sample_count):
                    opponent_card = random.sample(opponent_available_card, 2)
                    opponent = opponent_card[0] + opponent_card[1]
                    if judging(hand, opponent, board_card) == 0:
                        out_win_rate += 1
                out_win_rate = out_win_rate / settings.opponent_sample_count
                min_distance_index = 0
                min_distance = 10000
                for i in range(settings.river_cluster_count):
                    distance = math.pow(self.centroids_river[i][0] - out_win_rate, 2)
                    # distance = emd(np.array(win_rate), np.array(centroids[i]), matrix)
                    if distance < min_distance:
                        # print(i)
                        min_distance_index = i
                        min_distance = distance
                temp_out[min_distance_index] += 1
            if self.normalize_flag:
                sum_temp_out = sum(temp_out)
                for i in range(len(temp_out)):
                    temp_out[i] = temp_out[i] / sum_temp_out
            matrix = self.computer_distance_matrix("turn")
            min_distance_index = 0
            min_distance = 10000
            for j in range(settings.turn_cluster_count):
                distance = emd(np.array(temp_out), np.array(self.centroids_turn[j]), matrix)
                if distance < min_distance:
                    # print(i)
                    min_distance_index = i
                    min_distance = distance
            out[min_distance_index] += 1
        if self.normalize_flag:
            sum_out = sum(out)
            for i in range(len(out)):
                out[i] = out[i] / sum_out
        return out

    def generate_flop_data_comb(self, hand, public,state):

        out = [0.0] * settings.turn_cluster_count
        turn_available_card = copy.deepcopy(self.cards)
        for card in state:
            turn_available_card.remove(card)

        for turn_card in turn_available_card:
            turn_board_card = public + turn_card
            river_available_card = copy.deepcopy(turn_available_card)
            river_available_card.remove(turn_card)
            temp_out = [0.0] * settings.river_cluster_count
            for river_card in river_available_card:
                board_card = turn_board_card + river_card
                opponent_available_card = copy.deepcopy(river_available_card)
                opponent_available_card.remove(river_card)
                out_win_rate = 0

                opponent_cards = list(combinations(opponent_available_card, 2))
                for card in opponent_cards:
                    opponent_card = list(card)
                    opponent = opponent_card[0] + opponent_card[1]
                    if judging(hand, opponent, board_card) == 0:
                        out_win_rate += 1
                out_win_rate = out_win_rate / len(opponent_cards)
                min_distance_index = 0
                min_distance = 10000
                for i in range(settings.river_cluster_count):
                    distance = math.pow(self.centroids_river[i][0] - out_win_rate, 2)
                    if distance < min_distance:
                        # print(i)
                        min_distance_index = i
                        min_distance = distance
                temp_out[min_distance_index] += 1
            if self.normalize_flag:
                sum_temp_out = sum(temp_out)
                for i in range(len(temp_out)):
                    temp_out[i] = temp_out[i] / sum_temp_out
            matrix = self.computer_distance_matrix("turn")
            min_distance_index = 0
            min_distance = 10000
            for j in range(settings.turn_cluster_count):
                distance = emd(np.array(temp_out), np.array(self.centroids_turn[j]), matrix)
                if distance < min_distance:
                    # print(i)
                    min_distance_index = j
                    min_distance = distance
            out[min_distance_index] += 1
        if self.normalize_flag:
            sum_out = sum(out)
            for i in range(len(out)):
                out[i] = out[i] / sum_out
        return out

    def generate_data(self):

        if self.comb_flag:
            all_state = list(combinations(self.cards, self.state_count))
            state_count = 0
            for state in all_state:
                state = list(state)
                print('state {0}:'.format(state_count))
                possible_hand_comb = list(combinations(state, settings.hold_card_count))
                hand_count = 0
                for hand in possible_hand_comb:
                    hand = list(hand)
                    print("--- {0} th hand".format(hand_count))
                    hand_card = hand[0] + hand[1]
                    board_card = ""
                    board = copy.deepcopy(state)
                    for card in hand:
                        board.remove(card)
                    for i in range(len(board)):
                        board_card = board_card + board[i]
                    if self.street == 'river':
                        output = self.generate_river_data_comb(hand_card,board_card,state)
                    elif self.street == 'turn':
                        output = self.generate_turn_data_comb(hand_card,board_card,state)
                    else:
                        output = self.generate_flop_data_comb(hand_card,board_card,state)
                    out_string = ''
                    for i in range(len(output)):
                        if i == len(output) - 1:
                            out_string = out_string + str(output[i])
                        else:
                            out_string = out_string + str(output[i]) + ","
                    # print('out_result:', out_string)
                    self.file.write(out_string + '\n')
                    hand_count += 1
                state_count += 1
            self.file.close()
        else:
            for k in range(self.sample_count):
                print("---- {0} count ----".format(k))
                output = []
                state = random.sample(self.cards, self.state_count)
                if self.street == 'river':
                    output = self.generate_river_data(state)
                elif self.street == 'turn':
                    output = self.generate_turn_data(state)
                elif self.street == 'flop':
                    output = self.generate_flop_data(state)
                else:
                    pass
                out_string = ''
                for i in range(len(output)):
                    if i == len(output) - 1:
                        out_string = out_string + str(output[i])
                    else:
                        out_string = out_string + str(output[i]) + ","
                print('out_result:', out_string)
                self.file.write(out_string + '\n')
            self.file.close()

if __name__ == "__main__":

    generate_data = GenerateData(street='flop', sample_count=1000, comb_flag= True, normalize_flag = False)
    generate_data.generate_data()

