# -*- coding:utf-8 -*-

class Card():
    # the basics

    def __init__(self):
        self.STR_RANKS = '23456789TJQKA'
        self.INT_RANKS = range(13)
        self.PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

        # converstion from string => int
        self.CHAR_RANK_TO_INT_RANK = dict(zip(list(self.STR_RANKS), self.INT_RANKS))
        self.CHAR_SUIT_TO_INT_SUIT = {
            's': 1,  # spades
            'h': 2,  # hearts
            'd': 4,  # diamonds
            'c': 8,  # clubs
        }
        self.INT_SUIT_TO_CHAR_SUIT = 'xshxdxxxc'

        # for pretty printing
        self.PRETTY_SUITS = {
            1: u"\u2660".encode('utf-8'),  # spades
            2: u"\u2764".encode('utf-8'),  # hearts
            4: u"\u2666".encode('utf-8'),  # diamonds
            8: u"\u2663".encode('utf-8')  # clubs
        }

        self.PRETTY_REDS = [2, 4]

    def new(self,string):
        """
        Converts Card string to binary integer representation of card, inspired by:

        http://www.suffecool.net/poker/evaluator.html
        """

        rank_char = string[0]
        suit_char = string[1]
        rank_int = self.CHAR_RANK_TO_INT_RANK[rank_char]
        suit_int = self.CHAR_SUIT_TO_INT_SUIT[suit_char]
        rank_prime = self.PRIMES[rank_int]

        bitrank = 1 << rank_int << 16
        suit = suit_int << 12
        rank = rank_int << 8

        return bitrank | suit | rank | rank_prime

    def int_to_str(self,card_int):
        rank_int = self.get_rank_int(card_int)
        suit_int = self.get_suit_int(card_int)
        return self.STR_RANKS[rank_int] + self.INT_SUIT_TO_CHAR_SUIT[suit_int]

    def get_rank_int(self,card_int):
        return (card_int >> 8) & 0xF

    def get_suit_int(self,card_int):
        return (card_int >> 12) & 0xF

    def get_bitrank_int(self,card_int):
        return (card_int >> 16) & 0x1FFF

    def get_prime(self, card_int):
        return card_int & 0x3F

    def hand_to_binary(self,card_strs):
        """
        Expects a list of cards as strings and returns a list
        of integers of same length corresponding to those strings.
        """
        bhand = []
        for c in card_strs:
            bhand.append(self.new(c))
        return bhand

    def prime_product_from_hand(self, card_ints):
        """
        Expects a list of cards in integer form.
        """
        product = 1
        for c in card_ints:
            product *= (c & 0xFF)

        return product

    def prime_product_from_rankbits(self,rankbits):
        product = 1
        for i in self.INT_RANKS:
            # if the ith bit is set
            if rankbits & (1 << i):
                product *= self.PRIMES[i]

        return product

    def int_to_binary(self,card_int):
        """
        For debugging purposes. Displays the binary number as a
        human readable string in groups of four digits.
        """
        bstr = bin(card_int)[2:][::-1]  # chop off the 0b and THEN reverse string
        output = list("".join(["0000" + "\t"] * 7) + "0000")

        for i in range(len(bstr)):
            output[i + int(i / 4)] = bstr[i]

        # output the string to console
        output.reverse()
        return "".join(output)

    def int_to_pretty_str(self,card_int):
        """
        Prints a single card
        """

        color = False
        try:
            from termcolor import colored
            ### for mac, linux: http://pypi.python.org/pypi/termcolor
            ### can use for windows: http://pypi.python.org/pypi/colorama
            color = True
        except ImportError:
            pass
        # suit and rank
        suit_int = self.get_suit_int(card_int)
        rank_int = self.get_rank_int(card_int)

        # if we need to color red
        s = self.PRETTY_SUITS[suit_int]
        if color and suit_int in self.PRETTY_REDS:
            s = colored(s, "red")
        r = self.STR_RANKS[rank_int]
        return " [ " + r + " " + s + " ] "

    def print_pretty_card(self,card_int):
        """
        Expects a single integer as input
        """
        print(self.int_to_pretty_str(card_int))

    def print_pretty_cards(self,card_ints):
        """
        Expects a list of cards in integer form.
        """
        output = " "
        for i in range(len(card_ints)):
            c = card_ints[i]
            if i != len(card_ints) - 1:
                output += self.int_to_pretty_str(c) + ","
            else:
                output += self.int_to_pretty_str(c) + " "

        print(output)

# test
if __name__ == "__main__":
    card = Card()
    print(card.new("As"))