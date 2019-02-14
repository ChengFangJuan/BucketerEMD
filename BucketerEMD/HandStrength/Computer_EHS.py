# -*- coding:utf-8 -*-
from __future__ import division
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.table import Table
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
from BucketerEMD.judging import judging
from CFR.cfr import Game
import random
import copy
card_to_string = CARD_TO_STRING()
Game = Game()
label = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
rank_index_map = {'A': 0, 'K': 1, 'Q': 2,
'J': 3, 'T': 4, '9': 5,
'8': 6, '7': 7, '6': 8,
'5': 9, '4': 10, '3': 11, '2': 12}


def computer_EHS(card, sample_count):
    win_count = 0
    draw_count = 0
    all_cards = get_all_cards()
    available_card = copy.deepcopy(all_cards)
    for j in card:
        available_card.remove(j)

    for i in range(sample_count):
        print(" {0} th iter".format(i))
        board_opponent_card = random.sample(available_card, 7)
        board_card = board_opponent_card[:5]
        opponent_card = board_opponent_card[5:]

        card_string = list_to_string(card)
        board_string = list_to_string(board_card)
        opponent_string = list_to_string(opponent_card)
        if judging(card_string, opponent_string,board_string) == 0:
            win_count += 1
        elif judging(card_string, opponent_string, board_string) == 2:
            draw_count += 1

    win_rate = win_count / sample_count
    draw_rate = draw_count / sample_count
    EHS = win_rate + draw_rate / 2
    print("-----------------------------")
    print("win_rate:", win_rate)
    print("draw_rate:", draw_rate)
    print("EHS:", EHS)

    return EHS

def get_all_cards():
    card = card_to_string.rank_table[:settings.rank_count]
    flower = card_to_string.suit_table[:settings.suit_count]
    cards = []
    for i in card:
        for j in flower:
            cards.append(i + j)
    return cards

def list_to_string(list1):
    out = ''
    for i in list1:
        out = out + i
    return out

def get_color(frequency_old):
    frequency = frequency_old / 100
    if frequency >= 0.9:
        return 'green'
    elif frequency >= 0.75:
        return 'yellowgreen'
    elif frequency >= 0.5:
        return 'yellow'
    elif frequency >= 0.25:
        return 'orange'
    elif frequency >= 0.05:
        return 'orangered'
    else:
        return 'red'
def simplify_hand(hand):
    rank1 = hand[0][0]
    suit1 = hand[0][1]
    rank2 = hand[1][0]
    suit2 = hand[1][1]
    if rank1 == rank2:
        return rank1 + rank2

    hand = Game.get_higher_rank(rank1, rank2)
    hand += rank2 if hand==rank1 else rank1
    hand += 's' if suit1==suit2 else 'o'
    return hand

def get_result(sample_count):
    frequencies = dict()
    all_cards = get_all_cards()
    for card1 in all_cards:
        for card2 in all_cards:
            id = simplify_hand([card1,card2])
            if card1 == card2:
                frequencies[id] = 0.0
            else:
                frequencies[id] = computer_EHS([card1,card2], sample_count) * 100
    return frequencies


def plot_show(sample_count):
    fig, ax = plt.subplots()
    ax.set_axis_off()
    tb = Table(ax, bbox=[0, 0, 1, 1])

    nrows, ncols = len(label), len(label)
    width, height = 1.0 / ncols, 1.0 / nrows

    # Add cells
    frequencies = get_result(sample_count)
    for hand, val in frequencies.items():
        i, j = rank_index_map[hand[0]], rank_index_map[hand[1]]
        if len(hand) == 3 and hand[2] == 'o':
            i, j = j, i
        color = get_color(val)
        tb.add_cell(i + 1, j, width, height, text=str(round(val,2)),
                    loc='center', facecolor=color)

    # Row Labels...
    for i in range(len(label)):
        tb.add_cell(i + 1, -1, width, height, text=label[i], loc='right',
                    edgecolor='none', facecolor='none')
    # Column Labels...
    for j in range(len(label)):
        tb.add_cell(0, j, width, height / 2, text=label[j], loc='center',
                    edgecolor='none', facecolor='none')
    ax.add_table(tb)
    plt.title("EHS")
    plt.show()



if __name__ == "__main__":
    card = ["Ah", "Qs"]
    # EHS = computer_EHS(card, 10000)
    plot_show(10000)
