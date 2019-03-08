# -*- coding:utf-8 -*-
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING
import BucketerEMD.settings as settings
from itertools import combinations
from scipy.special import comb
import copy



class HandIsomorphism():

    def __init__(self):
        self.rank_index_map = {'A': 13, 'K': 12, 'Q': 11,
                          'J': 10, 'T': 9, '9': 8,
                          '8': 7, '7': 6, '6': 5,
                          '5': 4, '4': 3, '3': 2, '2': 1}
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

    # card_list 表示牌的列表，元素为牌的rank编号，如[13], [13,1], 计算当个rank牌的索引
    def computer_M_rank_index(self, card_list):
        card_list.sort(reverse = True)
        temp_card_list = copy.deepcopy(card_list)
        if len(temp_card_list) == 1:
            out_index = temp_card_list[0]
        else:
            card = temp_card_list[0]
            temp_card_list.remove(card)
            # print("-----------",comb(card,len(card_list)))
            out_index = comb(card,len(card_list)) + self.computer_M_rank_index(temp_card_list)
        return out_index

    def test_M_rank_index(self):
        cards = self.get_all_cards()
        test_card_comb = list(combinations(cards,2))
        for card in test_card_comb:
            temp = []
            for i in card:
                temp.append(self.rank_index_map[i[0]])
            out_index = self.computer_M_rank_index(temp)
            print(out_index)

    # 计算K轮点数集组的索引，cards_list 表示双重列表，元素表示牌的rank编号，如[[13,2],[12,4,5]]
    def computer_rank_groups_index(self, cards_list):

        if len(cards_list) == 1:
            out_index = self.computer_M_rank_index(cards_list[0])
        



        pass


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
    HandIsomorphism.test_M_rank_index()
