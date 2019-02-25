# -*- coding:utf-8 -*-
from __future__ import print_function
from random import shuffle as rshuffle
from NeuralFicititiousSelfPlay.Leduc.cardmatrix import CardMatrix

class Card():
    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit
        _cm = CardMatrix()
        self._named_rank, self._named_suit = _cm.getCard(rank, suit)

    # 实例化类，打印类会输出此项内容
    def __str__(self):
        return str(self._named_rank) + ' ' \
               + str(self._named_suit) + ' ' \
               + str(self._rank) + ' ' \
               + str(self._suit)

    def _print_human_style(self):
        print(str(self._named_suit + ' ' + self._named_rank))

    @property # 限制范围
    def rank(self):
        return self._rank


class Deck():

    def __init__(self, size=6):
        assert size > 0 and size % 2 == 0, 'Deck size has to be an even number which is greater than 0.'
        self._size = size
        self._fill()
        self.fake_pub = Card(-1, -1)

    def _fill(self):
        cards_per_suit = int(self._size / 2)
        self._cards = [Card(rank, suit)
                       for rank in range(cards_per_suit)
                       for suit in range(2)]

    def shuffle(self):
        """Shuffle deck"""
        rshuffle(self._cards)

    def fake_pub_card(self):
        return self.fake_pub

    def pick_up(self):
        return self._cards.pop()

    def print_deck(self):
        for card in self._cards:
            print(card.__str__())
