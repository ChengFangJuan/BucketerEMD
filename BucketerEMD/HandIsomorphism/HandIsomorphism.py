# -*- coding:utf-8 -*-
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
from itertools import combinations
from scipy.special import comb



class HandIsomorphism():

    def __init__(self):
        self.rank_index_map = {'A': 0, 'K': 1, 'Q': 2,
                          'J': 3, 'T': 4, '9': 5,
                          '8': 6, '7': 7, '6': 8,
                          '5': 9, '4': 10, '3': 11, '2': 12}
        self.suit_table = ['h', 's', 'd', 'c']
        self.suit_index_map = {'h': 0, 's': 1, 'd': 2, 'c': 3}
        self.card_to_string = CARD_TO_STRING()


    def get_all_cards(self):
        card = self.card_to_string.rank_table[:settings.rank_count]
        flower = self.card_to_string.suit_table[:settings.suit_count]
        cards = []
        for i in card:
            for j in flower:
                cards.append(i + j)
        return cards

    # card_list 表示牌的列表，元素为字符串，如A, 计算当个rank牌的索引
    def computer_single_rank_card_index(self, card_list):
        M_rank = []
        card_index = 0
        card_number = len(card_list)
        for card in card_list:
            M_rank.append(self.rank_index_map[card])
        M_rank.sort(reverse=True)

        if card_number == 1:
            card_index = M_rank[0]
        else:
            for i in range(1, card_number+1):
                if M_rank[i-1] < card_number -i + 1:
                    card_index = card_index + 0
                else:
                    card_index = card_index + comb(M_rank[i-1], card_number-i+1)
        return card_index

    def computer_card_index(self, card):
        pass









if __name__ == "__main__":
    HandIsomorphism = HandIsomorphism()
