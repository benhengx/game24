# -*- coding: utf-8 -*-


from __future__ import absolute_import, print_function, division

import random
import sys

try:
    import builtins
    unichr = getattr(builtins, 'chr')
    unicode = getattr(builtins, 'str')
except ImportError:
    pass

from . import calc


HAND_RESULT_SOLVED = 's'
HAND_RESULT_HINTED = 'h'
HAND_RESULT_FAILED = 'f'

CARD_SPADES = 0x1f0a1
CARD_HEARTS = 0x1f0b1
CARD_DIAMONDS = 0x1f0c1
CARD_CLUBS = 0x1f0d1


class Card(object):
    '''card is uniquely identified by the unicode code point value (self.code)
    self.integer is the integer value the card represents'''
    def __init__(self, code, integer):
        self.code = code
        self.integer = integer

    def __str__(self):
        if sys.version < '3':
            return unichr(self.code).encode('utf-8')
        else:
            return unichr(self.code)

    def __unicode__(self):
        return unichr(self.code)

    def __repr__(self):
        return repr(self.__unicode__())


class Hand(object):
    '''a hand is a number of cards the program randomly generates or 
    provided by the user to compute the target, the hand also records
    the result of user'''
    def __init__(self, cards, target=24):
        self.cards = cards
        self.target = target

        self.integers = [c.integer for c in cards]
        self.answers = calc.solve(self.integers, target)
        self.result = HAND_RESULT_FAILED

        self._hinti = 0
        self._hinted = False

    def str_cards(self):
        return '  '.join([str(card) for card in self.cards])

    def str_answer(self):
        return '\n'.join([str(expr) for expr in self.answers])

    def str_hint(self):
        if self.answers:
            if self._hinti == len(self.answers):
                self._hinti = 0
            hint = self.answers[self._hinti].str_hint()
            self._hinti += 1
            return hint
        return ''

    def hinted(self):
        self._hinted = True

    def solved(self):
        if self._hinted:
            self.result = HAND_RESULT_HINTED
        else:
            self.result = HAND_RESULT_SOLVED


class Game(object):
    '''24 game with one set of playing cards'''

    def __init__(self, target=24, count=4, face2ten=False):
        self.target = target
        self.count = count
        self.face2ten = face2ten

        self.seti = 0

        self.reset()

    def reset(self):
        self.cards = []
        self.hands = []

        random.seed()

        for i in range(13):
            integer = i + 1
            if self.face2ten and i in (10, 11, 12):
                integer = 10

            for j in (CARD_SPADES, CARD_HEARTS, CARD_DIAMONDS, CARD_CLUBS):
                code = j + i
                if i in (11, 12):
                    # the card of C is not considered
                    code += 1
                self.cards.append(Card(code, integer))

        self.seti += 1

    def is_set_end(self):
        return len(self.cards) < self.count

    def new_hand(self):
        if self.is_set_end():
            return None

        cards = []
        for i in range(self.count):
            idx = random.randint(0, len(self.cards) - 1)
            cards.append(self.cards.pop(idx))
        hand = Hand(cards, target=self.target)
        self.hands.append(hand)
        return hand

