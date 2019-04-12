# -*- coding:utf-8 -*-
from __future__ import division
import random
import numpy as np
import matplotlib.pyplot as plt
import sys

FOLD = 0
CALL = 1
RAISE = 2

KUHN_DECK = [1, 2, 3]
LEDUC_DECK = [1, 1, 2, 2, 3, 3]


# Tracks the regret per game stage
class gameTreeNode(object):
    """
    gameState - Players card and history of actions taken
    regretSum - Total regret for opponent for moves not selected to reach gameState
    strategy - Actions weighted to make opponent regret equal for all actions
    strategySum - Total strategy for each action accumulated over iterations
    """

    def __init__(self, gameState, numChoices):
        self.gameState = gameState
        self.actions = numChoices
        self.regretSum = [0.0] * numChoices
        self.strategy = [0.0] * numChoices
        self.strategySum = [0.0] * numChoices

    # Returns the least regretful strategy as defined by cfr
    def getStrategy(self, probability):
        sum = 0
        # Sum all positive strategies
        for i in range(self.actions):
            self.strategy[i] = self.regretSum[i] if self.regretSum[i] > 0 else 0
            sum += self.strategy[i]
        # Gives percentage to do one strategy over the other
        for i in range(self.actions):
            if sum > 0:
                self.strategy[i] /= sum
            else:
                self.strategy[i] = 1.0 / self.actions
            # probability = percentage chance to reach this game state
            self.strategySum[i] += self.strategy[i] * probability
        return self.strategy

    def getAverageStrategy(self):
        averageStrategy = [0.0] * self.actions
        sum = 0
        for i in range(self.actions):
            sum += self.strategySum[i]
        for i in range(self.actions):
            if sum > 0:
                averageStrategy[i] = self.strategySum[i] / sum
            else:
                averageStrategy[i] = 1.0 / self.actions
        return averageStrategy


class PokerTrainer(object):
    # Save game type
    # Initialize a game tree history
    def __init__(self, game):
        self.game = game
        if self.game == "kuhn":
            self.cards = KUHN_DECK
        elif self.game == "leduc":
            self.cards = LEDUC_DECK
        self.gameTree = {}
        self.save_strategy_file = open("strategy.txt",'w')

    # Trains the AI to decide on an optimal, Nash EQ strategy
    def train(self, iterations):
        # Called from main function, uses saved game type
        # Set initial utility to float zero
        utility = 0.0
        pre_strategy = self.computer_result()
        strategy_delta = []
        Information_set_count = []
        for i in range(1,iterations+1):
            # Randomizes array
            random.shuffle(self.cards) # 重新排列6张牌的顺序
            utility += self.cfr("", 1.0, 1.0, 0, False)

            if i % 100 == 0:
                new_strategy = self.computer_result()
                sum_delta_value = 0
                for state, strategy in new_strategy.items():
                    if state not in pre_strategy:
                        pre_strategy[state] = [1/len(strategy)] * len(strategy)
                    pre_strategy_ = np.array(pre_strategy[state])
                    new_strategy_ = np.array(strategy)
                    delta_value = np.square(new_strategy_-pre_strategy_).sum()
                    sum_delta_value += np.sqrt(delta_value)
                pre_strategy = new_strategy
                if sum_delta_value <= 2:
                    strategy_delta.append(sum_delta_value)
                Information_set_count.append(len(pre_strategy))
                print("============ iter count {0} ============".format(i))
                print("Information set count :", len(pre_strategy))
                print("Strategy delta :",sum_delta_value)

        # Print Outcome/winnings and each individual percentage to performt hat action
        print("Iterations:", iterations)
        print("Average utility: ", utility / iterations)
        print("game state count:", len(self.gameTree))
        # print("Strategy:")
        for gameState in sorted(self.gameTree.keys()):
            averageStrategy = self.gameTree[gameState].getAverageStrategy()
            self.save_strategy_file.write(gameState + ":" + str(averageStrategy) + "\n")
            # print(gameState,averageStrategy)

        f1, ax1 = plt.subplots(figsize=(14, 10))
        ax1.plot(strategy_delta, label='strategy delta')
        plt.legend()
        plt.xlabel("iter count")
        plt.ylabel("strategy delta")
        # plt.subplot(3,1,2)
        f2, ax2 = plt.subplots(figsize=(14, 10))
        ax2.plot(Information_set_count, label='information set num')
        plt.legend()
        plt.xlabel("iter count")
        plt.ylabel("information set num")
        f1.savefig('strategy_delta.png', dpi=100, bbox_inches='tight')
        f2.savefig('information_set_num.png', dpi=100, bbox_inches='tight')


    def computer_result(self):
        strategy_dict = dict()
        for gameState in sorted(self.gameTree.keys()):
            averageStrategy = self.gameTree[gameState].getAverageStrategy()
            strategy_dict[gameState] = averageStrategy
        return strategy_dict


    # Calculates one step of Counterfactual regret
    # 其中history表示历史动作，p0，p1表示到达状态的概率，stage表示是否为第二轮押注，roundCounter 每回合执行动作数
    def cfr(self, history, p0, p1, roundCounter, stage2):
        # Finds number result of utility gained for play
        result = self.evaluateGame(history) # history表示历史的状态，即决策点的状态，返回游戏是否结束，None表示没有结束

        # If it was a terminal state, return the result
        if not result is None:
            return result

        currentPlayer = roundCounter % 2  # 表示目前执行玩家
        gameState = None

        # Define current player and append to history
        # Why not just track player as a parameter to pass through the recursive call
        if self.game == "kuhn":
            gameState = str(self.cards[currentPlayer]) + history
        elif self.game == "leduc":
            if not stage2:
                gameState = str(self.cards[currentPlayer]) + history
            else:

                gameState = str(self.cards[currentPlayer]) + str(self.cards[2]) + history

        # If the current game state has already existed
        # Then create a pointer to the node for the same state
        actions = 3
        if roundCounter == 2 and (history[-2:] == 'rr' or history[-2:] == 'cr'):
            actions = 2

        if gameState in self.gameTree:
            node = self.gameTree[gameState]
        # Else create the state for the current game state
        else:
            node = gameTreeNode(gameState, actions)

        utilities = [0.0] * actions
        self.gameTree[gameState] = node

        # Returns the percentage to reach the next strategy steps.
        strategy = node.getStrategy(p0 if currentPlayer == 0 else p1)
        totalUtility = 0.0
        for i in range(actions):
            # Update history and recursive call to function to decide next step
            nextHistory = history
            nextStage = stage2
            if i == FOLD:
                nextHistory += "f"
            elif i == CALL:
                nextHistory += "c"
            elif i == RAISE:
                nextHistory += "r"
            else:
                return None

            # Use updated probability to reach the next game state
            if currentPlayer == 0:
                nextP0 = p0 * strategy[i]
                nextP1 = p1
            else:
                nextP0 = p0
                nextP1 = p1 * strategy[i]

            # Update the turn counter so we know the player
            nextRoundCounter = roundCounter
            if (nextHistory[-2:] == "cc" or nextHistory[-2:] == "rc") and roundCounter != 0:
                # if (history[:3] == "pbb" or history[:3] =="brb"):
                nextRoundCounter = 0
            else:
                nextRoundCounter += 1

            if nextRoundCounter == 0:
                nextStage = not nextStage
            if nextStage and (nextHistory[-3:] == "crc" or nextHistory[-3:] == "rrc"):
                utilities[i] = self.cfr(nextHistory, nextP0, nextP1, nextRoundCounter, nextStage)
            else:
                utilities[i] = -self.cfr(nextHistory, nextP0, nextP1, nextRoundCounter, nextStage)

            # Sum resulting utility for each strategy
            totalUtility += utilities[i] * strategy[i]
        for i in range(actions):
            # Diff between gain for an action vs total possible gain?
            regret = utilities[i] - totalUtility
            # Regret for choosing that decision
            node.regretSum[i] += regret * (p1 if currentPlayer == 0 else p0)

        return totalUtility

    # returns the value of the game if it is terminal
    # else returns None
    def evaluateGame(self, history):
        # Returns earnings if it is a terminal state and using Kuhn Poker
        # Returns None if not terminal
        if self.game == "kuhn":
            return self.kuhnEval(history)

        elif self.game == "leduc":
            return self.leducEval(history)

        # Returns none if not a game (never a case)
        # Or when not a terminal state (no conditions met to end game)

    # Returns the value of the play in Kuhn Poker if it is a terminal state
    def kuhnEval(self, history):
        # Defines the player and opponent for current turn
        plays = len(history)
        if plays < 2:
            return None
        player = plays % 2
        opponent = 1 - player

        # If not terminal
        # Same action leads to a showdown
        # Checks the last two moves
        showdown = (history[-1] == history[-2])
        leadingBet = (history[-2] == "b")
        if showdown:
            winner = self.cards[player] > self.cards[opponent]
            if leadingBet:
                return 2 if winner else -2
            return 1 if winner else -1
        # If not leadingBet and showdown, it's a bet pass
        # if not leading bet, it was a pass bet and we should return None
        return 1 if leadingBet else None

    # Returns the value of the play in Leduc Poker if it is a terminal state
    def leducEval(self, history):
        plays = len(history) # history 表示历史动作，大于等于2才可能结束游戏
        if plays < 1:
            return None

        # Terminal in round 1, so we can short circuit
        # vars for readability
        round1f = history[:1] == "f"
        if (round1f):
            return 0.5

        round1cf = (history[:2] == "cf") or (history[:2] == "rf") or (history[:3] == "crf")
        if (round1cf):
            return 1

        round1rrf = history[:3] == "rrf"
        if round1rrf:
            return 2

        # Not terminal in round 1
        # Round 1 is just checks
        round1cc = (history[:2] == "cc")
        # Create var, updated only if not pp. Reduces linear checks
        round1cr = False
        round1rr = False
        # Default to pp pot size and index
        round2startIndex = 2
        round1pot = 1
        # Round1 is a bet call
        if not round1cc:
            round1cr = (history[:2] == 'cr') or (history[:2] == 'rc')
            round1rr = history[:2] == 'rr'
            leadingPass = history[0] == "c"
            if round1rr:
                round2startIndex = 3
                round1pot = 3

            if round1cr:
                if leadingPass:
                    round2startIndex = 3
                else:
                    round2startIndex = 2
                round1pot = 2

        # Round 1 unfinished (eg only 1 move is done)
        if not (round1cc or round1cr or round1rr):
            return None

        round2History = history[round2startIndex:] # 表示第二回合的历史动作

        round2Plays = len(round2History)

        if round2Plays < 1:
            return None

        # Bet pass in round 2
        round2f = (round2History == "f")or(round2History == "cf")or(round2History == "crf")or(round2History == "rf")
        if (round2f):
            return round1pot

        # Bet raise pass in round 2
        round2rf = round2History == "rrf"
        if (round2rf):
            return round1pot + 1

        player = round2Plays % 2
        opponent = 1 - player

        winner = (self.cards[player] == self.cards[2] or (
                    self.cards[opponent] != self.cards[2] and self.cards[player] > self.cards[opponent]))
        tie = self.cards[player] == self.cards[opponent]
        # Check to showdown
        round2cc = (round2History == "cc")
        if round2cc:
            if tie:
                return 0
            return round1pot if winner else -round1pot

        # Bet to showdown
        round2cr = (round2History == "crc") or (round2History == "rc")
        if round2cr:
            if tie:
                return 0
            # return 4+round1pot if winner else -(4+round1pot)
            return (round1pot+1) if winner else -(round1pot+1)

        # Betraise to showdown
        round2rr = round2History == "rrc"
        if round2rr:
            if tie:
                return 0
            # return 8+round1pot if winner else -(8+round1pot)
            return (round1pot+2) if winner else -(round1pot+2)


def main():
    # Takes input of game type
    trainer = PokerTrainer("leduc")
    random.seed(1234)
    # Number of trials
    trainer.train(1000000)
    trainer.save_strategy_file.close()


if __name__ == "__main__":
    main()