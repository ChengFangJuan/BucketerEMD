# -*- coding:utf-8 -*-

from random import shuffle
from Holdem.deuces.card import Card

class Deck():

    def __init__(self):
        # self.shuffle()
        self._FULL_DECK = []
        self.card = Card()

    # 打乱牌的顺序
    def shuffle(self):
        # and then shuffle
        self.cards = self.GetFullDeck() # 所有牌的二进制表示
        shuffle(self.cards)

    # 发牌
    def draw(self, n=1):
        if n == 1:
            return self.cards.pop(0)

        cards = []
        for i in range(n):
            cards.append(self.draw())
        return cards

    def __str__(self):
        return self.card.print_pretty_cards(self.cards)

    def GetFullDeck(self):
        if self._FULL_DECK:
            return list(self._FULL_DECK)

        # create the standard 52 card deck
        for rank in self.card.STR_RANKS:
            for suit,val in self.card.CHAR_SUIT_TO_INT_SUIT.items():
                self._FULL_DECK.append(self.card.new(rank + suit))

        return list(self._FULL_DECK)

# test
if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()
    print(deck.draw(1))
    print(deck.draw(2))