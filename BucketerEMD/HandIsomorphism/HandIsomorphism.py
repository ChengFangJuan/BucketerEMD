# -*- coding:utf-8 -*-
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
from itertools import combinations
from scipy.special import comb



class HandIsomorphism():

    def __init__(self):
        self.rank_index_map = {'A': 1, 'K': 2, 'Q': 3,
                          'J': 4, 'T': 5, '9': 6,
                          '8': 7, '7': 8, '6': 9,
                          '5': 10, '4': 11, '3': 12, '2': 13}
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

    #计算单个回合的牌的index，card 列表表示 如['As', 'Ah']
    def computer_preround_card_index(self,card):
        suit_card = dict()
        suit_index = dict()
        out_index = 0
        for i in card:
            if i[1] not in suit_card:
                suit_card[i[1]] = []
            suit_card[i[1]].append(i[0])
        for id, value in suit_card.items():
            suit_index[id] = self.computer_single_rank_card_index(value)

        for id, value in suit_index.items():
            out_index += comb(13,len(suit_card[id])) * value

        return out_index

    def test_pre_round_index(self):
        all_cards = self.get_all_cards()
        available_cards = list(combinations(all_cards,2))
        print("available cards count:", comb(len(all_cards),2))
        all_card_index = []
        for card in available_cards:
            card_ = list(card)
            temp_index = self.computer_preround_card_index(card_)
            print("--- card {0} --- index {1}".format(card_, temp_index))
            if temp_index not in all_card_index:
                all_card_index.append(temp_index)
        print("cards index count:", len(all_card_index))






    # 计算牌的index， card的表示是列表, [['As','Ah'],[],[],[]], 最大4个元素，表示4个回合的牌
    def computer_card_index(self, card):
        pass









if __name__ == "__main__":
    HandIsomorphism = HandIsomorphism()
    HandIsomorphism.test_pre_round_index()
