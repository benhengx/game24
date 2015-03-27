#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import sys
import argparse
import readline
import random
import traceback

try:
    import builtins
    raw_input = getattr(builtins, 'input')
except ImportError:
    pass

from game24 import calc, game


MSG_MENU_MAIN = '''1. Play (p)
2. Check answer (c)
3. Quit (q)'''

MSG_MENU_PLAY = '''1. Definitely no solutions (n)
2. Give me a hint (h)
3. I gave up, show me the answer (s)
4. Back to the main menu (b)
5. Quit the game (q)'''

MSG_MENU_SET_END = '''1. One more set (n)
2. Back to the main menu (b)
3. Quit the game (q)'''

MSG_MENU_PLAY_RIGHT = '''1. Try other solutions (t)
2. Next hand (n)
3. Show me the answers (s)
4. Quit the game (q)'''

MSG_SELECT = 'Your choice: '
MSG_INVALID_INPUT = 'Invalid input!'

MSG_MENU_HAND_END = '''1. One more hand (n)
2. Quit this set, back to the main menu (b)
3. Quit the game (q)'''

MSG_SELECT = 'Your choice: '
MSG_INVALID_INPUT = 'Invalid input!'
MSG_INVALID_INTEGER = 'Invalid integer: %s'

MSG_PLAY_NEW_SET = 'Set %d'
MSG_PLAY_NEW_HAND = 'Hand %d: %s'
MSG_PLAY_INPUT_EXPR = 'Input your solution or one of the above choices: '
MSG_PLAY_RIGHT = 'Good Job!'
MSG_PLAY_FIND_BUG = '''Great Job!
You not only solved the problem, but also found a bug!
Please report to me with the cards and your solution if you don't mind.'''
MSG_PLAY_WRONG = "Sorry! It's not correct!"
MSG_PLAY_NO_ANSWER = 'Seems no solutions'
MSG_PLAY_NO_CARDS = 'Set end, your result' 

MSG_INPUT_NUMBERS = 'Please input %d integers: '

INPUT_EOF = '\x00'


class GameConsole(game.Game):
    def __init__(self, target=24, count=4, face2ten=False, showcard=False):
        super(GameConsole, self).__init__(target, count, face2ten)
        self.showcard = showcard

    @staticmethod
    def raw_input_ex(prompt='', default=''):
        '''enhance raw_input to support default input and also flat EOF'''
        try:
            readline.set_startup_hook(lambda: readline.insert_text(default))
            try:
                return raw_input(prompt)
            finally:
                readline.set_startup_hook()

        except EOFError:
            return INPUT_EOF

    @staticmethod
    def print_title(title, dechar='', delen=50):
        print(dechar * delen)
        print(title)
        print(dechar * delen)

    @staticmethod
    def ui_menu(menu, choices, eof=True):
        '''show a menu, and return the selection'''
        GameConsole.print_title(menu, dechar='-')
        while True:
            r = GameConsole.raw_input_ex(MSG_SELECT).strip()
            if r.lower() in choices or (eof and r == INPUT_EOF):
                print()
                return r
            print(MSG_INVALID_INPUT)

    def ui_check_answer(self):
        '''show answers for user provided integers'''
        while True:
            r = self.raw_input_ex(MSG_INPUT_NUMBERS % self.count).strip()
            try:
                integers = [int(s) for s in r.strip().split()]
            except ValueError:
                print(MSG_INVALID_INPUT)
                continue

            if len(integers) != self.count:
                print(MSG_INVALID_INPUT)
                continue
            break

        answers = calc.solve(integers, self.target)
        if answers:
            s = '\n'.join([str(expr) for expr in answers])
        else:
            s = MSG_PLAY_NO_ANSWER
        self.print_title(s)

    def main(self):
        '''the main entry of the game console'''
        choices = '1p2c3q'
        while True:
            r = self.ui_menu(MSG_MENU_MAIN, choices)
            if r in '1p':
                self.play()

            elif r in '2c':
                self.ui_check_answer()

            elif r in ('3q' + INPUT_EOF):
                return

    def print_result(self):
        solved = 0
        failed = 0
        hinted = 0
        for hand in self.hands:
            if hand.result == game.HAND_RESULT_SOLVED:
                solved += 1
            elif hand.result == game.HAND_RESULT_HINTED:
                hinted += 1
            elif hand.result == game.HAND_RESULT_FAILED:
                failed += 1
        print()
        print('Total %d hands solved' % solved)
        print('Total %d hands solved with hint' % hinted)
        print('Total %d hands failed to solve' % failed)
        print()

    def ui_menu_and_expr(self, menu, choices, eof=True):
        hand_ints = self.hands[-1].integers
        self.print_title(menu, dechar='-')
        while True:
            r = self.raw_input_ex(MSG_PLAY_INPUT_EXPR).strip()
            if r.lower() in choices or (eof and r == INPUT_EOF):
                print()
                return r

            try:
                expr = calc.parse(r)
            except ValueError as e:
                print(str(e))
                continue

            integers = expr.get_integers()
            for i in integers:
                if i not in hand_ints:
                    print(MSG_INVALID_INTEGER % i)
                    break
            else:
                return expr

    def play(self):
        while True:
            if not self.hands:
                self.print_title(MSG_PLAY_NEW_SET % self.seti, dechar='*')

            hand = self.new_hand()
            if not hand:
                # no enough cards for a new hand
                self.print_title(MSG_PLAY_NO_CARDS, dechar='*')
                self.print_result()

                choices = '1n2b3q'
                r = self.ui_menu(MSG_MENU_SET_END, choices)
                if r in '1n':
                    # renew the set
                    self.reset()
                    continue

                elif r in ('2b' + INPUT_EOF):
                    # back to the main menu
                    return

                elif r in '3q':
                    sys.exit(0)

            print()
            if self.showcard:
                sc = hand.str_cards()
            else:
                sc = ' '.join([str(i) for i in hand.integers])
            self.print_title(MSG_PLAY_NEW_HAND % (len(self.hands), sc), 
                                                            dechar='+')
            print()
            while True:
                choices = '1n2h3s4b5q'
                r = self.ui_menu_and_expr(MSG_MENU_PLAY, choices)
                if isinstance(r, calc.Expr):
                    expr = r
                    if expr.value == self.target:
                        hand.solved()
                        if expr not in hand.answers:
                            s = MSG_PLAY_FIND_BUG
                        else:
                            s = MSG_PLAY_RIGHT
                        self.print_title(s)

                        choices = '1t2n3s4q'
                        r = self.ui_menu(MSG_MENU_PLAY_RIGHT, choices, eof=False)
                        if r in '1t':
                            continue
                        elif r in '2n':
                            break
                        elif r in '3s':
                            self.print_title(hand.str_answer())
                        elif r in '4q':
                            sys.exit(0)

                    else:
                        self.print_title(MSG_PLAY_WRONG)
                        continue

                elif r in '1n':
                    # no answer
                    if hand.answers:
                        self.print_title(MSG_PLAY_WRONG)
                        continue
                    else:
                        hand.solved()
                        self.print_title(MSG_PLAY_RIGHT)

                elif r in '2h':
                    # show a hint
                    if hand.answers:
                        hand.hinted()
                        self.print_title(hand.str_hint())
                        continue
                    else:
                        self.print_title(MSG_PLAY_NO_ANSWER)

                elif r in '3s':
                    # show the answer
                    if hand.answers:
                        s = hand.str_answer()
                    else:
                        s = MSG_PLAY_NO_ANSWER
                    self.print_title(s)

                elif r in ('4b' + INPUT_EOF):
                    # back to the main menu
                    return

                elif r in '5q':
                    sys.exit(0)

                # this hand is end
                break


def arg_parse():
    parser = argparse.ArgumentParser(description='Play the 24 Game')
    parser.add_argument('-c', type=int, default=4, dest='count',
            help='the number of integers to play with, default=4')
    parser.add_argument('-C', action='store_true', dest='showcard',
            help='show cards instead of integers under interactive mode')
    parser.add_argument('-d', action='store_true', dest='debug',
            help='enable debug output')
    parser.add_argument('-i', action='store_true', dest='interactive',
            help='interactive mode, all positional integers arguments omitted')
    parser.add_argument('-N', action='store_true', dest='face2ten',
            help='under interactive mode, set J Q K to 10, default=11,12,13')
    parser.add_argument('-t', type=int, default=24, dest='target',
            help='the game target, default=24')
    parser.add_argument('integers', nargs='*')

    r = parser.parse_args()

    if not r.interactive and len(r.integers) == 0:
        r.interactive = True

    elif not r.interactive and len(r.integers) != 1:
        if len(r.integers) != r.count:
            parser.error('invalid number of integers provided, expect %d' % 
                                                                    r.count)

        err_nums = [s for s in r.integers if not s.isdigit()]
        if err_nums:
            parser.error('invalid integers: %s' % str(err_nums))

        r.integers = [int(s) for s in r.integers]

        err_nums = [i for i in r.integers if i < 1 or 
                        i > (r.face2ten and 10 or 13)]
        if err_nums:
            parser.error('invalid integers: %s' % str(err_nums))

    return r


def main():
    args = arg_parse()
    try:
        if args.interactive:
            gc = GameConsole(args.target, args.count, 
                        args.face2ten, args.showcard)
            gc.main()

        elif len(args.integers) == 1:
            # parse expression
            expr = calc.parse(args.integers[0])
            if args.debug:
                print(repr(expr))
                print(str(expr))
            print(expr.value)

        else:
            # solve
            exprs = calc.solve(args.integers, args.target)
            if not exprs:
                print(MSG_PLAY_NO_ANSWER)
            else:
                for expr in exprs:
                    print(args.debug and repr(expr) or str(expr))

        sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as e:
        if args.debug:
            traceback.print_exc()
        else:
            print(str(e), file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()

