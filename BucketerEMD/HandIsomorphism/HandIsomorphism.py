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
        self.cards = self.get_all_cards()


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

    # 计算K轮点数集组的索引，cards_list 表示双重列表，元素表示牌的rank编号，如[[13,2],[12,4,5]]
    def computer_rank_groups_index(self, cards_list, all_count):
        temp_cards_list = copy.deepcopy(cards_list)
        if len(temp_cards_list) == 1:
            out_index = self.computer_M_rank_index(temp_cards_list[0])
        else:
            card = temp_cards_list[0]
            temp_cards_list.remove(card)
            out_index = self.computer_M_rank_index(card) + \
                comb(all_count,len(card)) * self.computer_rank_groups_index(temp_cards_list, all_count - len(card))
        return out_index

    def computer_card_index(self,card):
        pass

    def test_M_rank_index(self):
        cards = self.get_all_cards()
        test_card_comb = list(combinations(cards, 2))
        for card in test_card_comb:
            temp = []
            for i in card:
                temp.append(self.rank_index_map[i[0]])
            out_index = self.computer_M_rank_index(temp)
            print(out_index)

    def test_rank_groups_index(self):
        one_round_card = list(combinations(self.cards,2))
        for one_card in one_round_card:
            two_available_card = copy.deepcopy(self.cards)
            for i in range(len(one_card)):
                two_available_card.remove(one_card[i])
            two_round_card = list(combinations(two_available_card,3))
            for two_card in two_round_card:
                test_card_comb = []
                one_temp = []
                two_temp = []
                for i in one_card:
                    one_temp.append(self.rank_index_map[i[0]])
                test_card_comb.append(one_temp)
                for i in two_card:
                    two_temp.append(self.rank_index_map[i[0]])
                test_card_comb.append(two_temp)

                out_index = self.computer_rank_groups_index(test_card_comb, 13)
                print(out_index)



if __name__ == "__main__":
    HandIsomorphism = HandIsomorphism()
    # HandIsomorphism.test_M_rank_index()
    HandIsomorphism.test_rank_groups_index()
