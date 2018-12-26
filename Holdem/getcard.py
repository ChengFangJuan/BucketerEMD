from Holdem.deuces.card import Card

nEnum = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
suits = ['c', 'd', 's', 'h']

class GetCard():

    def __init__(self, numLet, suit):

        """ Constructor accepts number [2-14] or letter (T,J,Q,K,A) of card and suit of card (c,d,s,h). """
        self.card = Card()
        if type(numLet) == int:
            if numLet < 2 or numLet > 14:
                raise Exception('Card number must be between 2 and 14 (inclusive).')
            self._numLet = numLet # 表示牌的rank
            for k in nEnum:
                if nEnum[k] == numLet:
                    self._numLet = k
        elif type(numLet) == str:
            if numLet.upper() not in nEnum:
                raise Exception("Card letter must be \'T\', \'J\', \'Q\', \'K\', or \'A\'.")
            self._numLet = numLet.upper()
        else:
            raise Exception('Card number/letter must be number or string.')

        if suit.lower() not in suits:
            raise Exception("Invalid suit. Valid suits are \'c\', \'d\', \'s\', and \'h\'.")
        self._suit = suit.lower() # 表示牌的花色

    def getNumber(self):
        # 得到牌的编号为2-14
        """ This method returns number of card. It converts letter to number if necesary. """
        if self._numLet in nEnum:
            return nEnum[self._numLet]
        return self._numLet

    def getSuit(self):
        # 得到牌的花色
        return self._suit

    def toInt(self):
        return self.card.new(str(self))  # returns int compatible with deuces library

    def __lt__(self, other):
        return self.getNumber() < other.getNumber()

    def __str__(self):
        return str(self._numLet) + self._suit