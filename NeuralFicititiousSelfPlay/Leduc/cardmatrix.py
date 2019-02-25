# -*- coding:utf-8 -*-
# 建立所有牌的矩阵
import numpy as np


class CardMatrix():
    """Matrix with all possible card ranks and suits from a 52 standard card deck"""

    def __init__(self):
        self._cardmatrix = np.array([['Ace', 'King', 'Queen', 'Jack', '10', '9', '8', '7', '6', '5', '4', '3', '2'],
                                     ['Heart', 'Spades', 'Cross', 'Diamonds']])

    def getCard(self, rank, suit):
        return self._cardmatrix[0][rank], self._cardmatrix[1][suit]