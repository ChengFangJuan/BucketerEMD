
from Holdem.deuces.card import Card
from Holdem.deuces.deck import Deck
from Holdem.deuces.evaluator import Evaluator

class GO():
    def __init__(self):
        self.set_card = Card()
        # create an evaluator
        self.evaluator = Evaluator()
        self.deck = Deck()

    def evaluator_card(self):
        # create a card
        card = self.set_card.new('Qh')
        # create a board and hole cards
        board = [self.set_card.new('2h'),self.set_card.new('2s'),self.set_card.new('Jc')]
        hand = [self.set_card.new('Qs'), self.set_card.new('Th')]
        # pretty print cards to console
        self.set_card.print_pretty_cards(board + hand)
        # and rank your hand
        rank = self.evaluator.evaluate(board, hand)
        print("Rank for your hand is: %d" % rank)
        # or for random cards or games, create a deck
        print("Dealing a new hand...")

        board = self.deck.draw(5)
        player1_hand = self.deck.draw(2)
        player2_hand = self.deck.draw(2)

        print("The board:")
        self.set_card.print_pretty_cards(board)

        print("Player 1's cards:")
        self.set_card.print_pretty_cards(player1_hand)

        print("Player 2's cards:")
        self.set_card.print_pretty_cards(player2_hand)

        p1_score = self.evaluator.evaluate(board, player1_hand)
        p2_score = self.evaluator.evaluate(board, player2_hand)

        # bin the scores into classes
        p1_class = self.evaluator.get_rank_class(p1_score)
        p2_class = self.evaluator.get_rank_class(p2_score)

        # or get a human-friendly string to describe the score
        print("Player 1 hand rank = %d (%s)" % (p1_score, self.evaluator.class_to_string(p1_class)))
        print("Player 2 hand rank = %d (%s)" % (p2_score, self.evaluator.class_to_string(p2_class)))

        # or just a summary of the entire hand
        hands = [player1_hand, player2_hand]
        self.evaluator.hand_summary(board, hands)


if __name__ == "__main__":
     go = GO()
     go.evaluator_card()