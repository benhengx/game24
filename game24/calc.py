# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

from fractions import Fraction

try:
    import __builtin__
    cmp = getattr(__builtin__, 'cmp')
except (ImportError, AttributeError):
    def cmp(x, y): return (x > y) - (x < y)

def opr_py2math(opr):
    return opr == '*' and '×' or (opr == '/' and '÷' or opr)


def opr2uni(opr):
    return opr in '+-' and '+' or '*'


def opr2orig(uni_opr, reverse=True):
    return reverse and (uni_opr == '+' and '-' or '/') or uni_opr


class BaseNumber(object):
    _index = 0
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def _detail_cmp(self, other):
        return self.value - other.value

    def __cmp__(self, other):
        c = self._index - other._index
        if c:
            return c
        return self._detail_cmp(other)

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0


class Number(BaseNumber):
    _index = 1


class Rand(object):
    def __init__(self, number, reverse=False):
        self.number = number
        self.reverse = reverse

    def __repr__(self):
        n = repr(self.number)
        if self.reverse:
            n = '^' + n
        return n

    def __str__(self):
        return repr(self)

    def __cmp__(self, other):
        if self.reverse != other.reverse:
            return self.reverse and 1 or -1

        elif type(self.number) != type(other.number):
            # Number comes before Expr
            return self.number._index - other.number._index

        else:
            return self.number.__cmp__(other.number)

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0


class Expr(BaseNumber):
    '''An arithmatic expression with an operator and multi operands.
    self.opr is the unified operator (either + or *)
    self.rands is a list of Rand'''
    _index = 2


    def __init__(self, opr):
        self.opr = opr
        self.rands = []

        self._value = 0

    def set_value(self):
        if self.rands:
            self.rands.sort()
            assert(not self.rands[0].reverse)
            self._value = self.rands[0].number.value

        for rand in self.rands[1:]:
            if self.opr == '+' and not rand.reverse:
                self._value += rand.number.value

            elif self.opr == '+' and rand.reverse:
                self._value -= rand.number.value

            elif self.opr == '*' and not rand.reverse:
                self._value *= rand.number.value

            elif self.opr == '*' and rand.reverse and rand.number.value:
                self._value = Fraction(self._value, rand.number.value)

            else:
                self._value = None

    @property
    def value(self):
        return self._value

    def add(self, number, reverse=False):
        if isinstance(number, Expr) and self.opr == number.opr:
            return self.extend(number, reverse)

        if (reverse and ((self.opr == '*' and number.value == 1) or
                        (self.opr == '+' and number.value == 0))):
            # x / 1 is unified to x * 1, x - 0 unified to x + 0
            reverse = False

        self.rands.append(Rand(number, reverse))

        self.set_value()

    def extend(self, expr, reverse=False):
        assert(self.opr == expr.opr)

        for rand in expr.rands:
            if not reverse:
                self.add(rand.number, rand.reverse)
            else:
                self.add(rand.number, not rand.reverse)

        self.set_value()

    def str_hint(self):
        # return a string of (x opr y)
        for rand in self.rands:
            if isinstance(rand.number, Expr):
                return rand.number.str_hint()
        else:
            return ('%s %s %s' % (str(self.rands[0].number), 
                opr2orig(self.opr, self.rands[1].reverse), 
                str(self.rands[1].number)))

    def get_integers(self):
        # return integers that composed the expr
        ints = []
        for rand in self.rands:
            if isinstance(rand.number, Expr):
                ints.extend(rand.number.get_integers())
            else:
                ints.append(rand.number.value)
        return ints

    def __repr__(self):
        return '<%s %s>' % (self.opr, repr(self.rands))

    def __str__(self):
        self.rands.sort()

        s = ''
        for rand in self.rands:
            rs = str(rand.number)
            if isinstance(rand.number, Expr) and self.opr == '*':
                rs = '(%s)' % rs

            if not s:
                s = rs
            else:
                opr = opr_py2math(opr2orig(self.opr, rand.reverse))
                s = '%s %s %s' % (s, opr, rs)
        return s

    def _detail_cmp(self, other):
        if self.opr != other.opr:
            return ord(self.opr) - ord(other.opr)

        elif len(self.rands) != len(other.rands):
            return len(self.rands) - len(other.rands)

        else:
            self.rands.sort()
            other.rands.sort()

            for i in range(len(self.rands)):
                c = self.rands[i].__cmp__(other.rands[i])
                if c:
                    return c
            return 0


def expr_create(left, opr, right):
    if opr in ('+', '*'):
        expr = Expr(opr)
        if isinstance(left, Number) or left.opr != opr:
            expr.add(left)
        else:
            expr.extend(left)

        if isinstance(right, Number) or right.opr != opr:
            expr.add(right)
        else:
            expr.extend(right)

    else:
        if (opr == '-' and left.value < right.value) or opr == 'r/':
            left, right = right, left

        uni_opr = opr == '-' and '+' or '*'
        if uni_opr == '*' and right.value == 0:
            return None

        expr = Expr(uni_opr)
        if isinstance(left, Number) or left.opr != uni_opr:
            expr.add(left)
        else:
            expr.extend(left)

        if isinstance(right, Number) or right.opr != uni_opr:
            expr.add(right, reverse=True)
        else:
            expr.extend(right, reverse=True)

    return expr


class State(object):
    '''State is a list of numbers created during calculating.
    Each number can either be a number or an expression
    '''
    def __init__(self, numbers):
        self.numbers = numbers
        self.numbers.sort()

    def __repr__(self):
        return '<state: %s>' % repr(self.numbers)

    def __str__(self):
        return str(self.numbers)

    def __cmp__(self, other):
        if len(self.numbers) != len(other.numbers):
            return len(self.numbers) - len(other.numbers)

        for i in range(len(self.numbers)):
            c = cmp(self.numbers[i], other.numbers[i])
            if c:
                return c
        return 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def is_computable(self):
        return len(self.numbers) > 1

    def compute(self):
        '''compute returns a list of child State by picking two 
        numbers from it and calculating to a new number then plus
        the remaining numbers'''
        if not self.is_computable():
            return None

        combs = []
        count = len(self.numbers)
        for i in range(count - 1):
            for j in range(i + 1, count):
                numbers = self.numbers[:]
                y,x = numbers.pop(j), numbers.pop(i)
                comb = State([x,y]), State(numbers)
                if comb not in combs:
                    combs.append(comb)

        child_states = []
        for comb in combs:
            x,y = comb[0].numbers
            numbers = comb[1].numbers
            new_number_values = []
            for opr in ('+', '-', '*', '/', 'r/'):
                expr = expr_create(x, opr, y)
                if (expr is None or expr.value is None or 
                        expr.value in new_number_values):
                    continue

                new_number_values.append(expr.value)

                new_numbers = numbers[:]
                new_numbers.append(expr)
                new_state = State(new_numbers)
                if not new_state in child_states:
                    child_states.append(new_state)

        return child_states


def solve(integers, target=24):
    '''return a list of Expr that compute to the target'''

    init_state = State([Number(i) for i in integers])

    cur_states = [init_state]
    while cur_states[0].is_computable():
        child_states = []
        for state in cur_states:
            child_states.extend(state.compute())
        cur_states = child_states

    exprs = []
    for state in cur_states:
        expr = state.numbers[0]
        if expr.value == target and expr not in exprs:
            exprs.append(expr)

    return exprs


class TokenReader(object):
    def __init__(self, solution):
        self.solution = solution
        self.cursor = 0
        self.cache = []

    def push(self, token):
        self.cache.append(token)

    def read(self):
        if self.cache:
            return self.cache.pop()

        chars = ('(', ')', '+', '-', '*', '/')
        token = ''
        digit = False
        i, s = self.cursor, self.solution
        while i < len(s):
            if s[i].isspace():
                if digit:
                    self.cursor = i + 1
                    return token
    
            elif s[i].isdigit():
                if not digit:
                    digit = True
                token += s[i]
    
            elif s[i] in chars:
                if digit:
                    self.cursor = i
                    return token
                else:
                    self.cursor = i + 1
                    return s[i]
    
            else:
                raise ValueError('Invalid character: %s' % s[i])
    
            i += 1

        self.cursor = i
        return token

    def unparsed(self):
        s = self.solution[self.cursor:]
        if self.cache:
            s = ' '.join(self.cache) + ' ' + s
        return s


def read_expr(tr, exit_at_right_p=False, exit_at_one_expr=False):
    '''a simple arithmatic expression parser. 
    during parsing, the parser can be in one of the following states:
    n - operand expected as the next token
    o - operator expected as the next token
    x - expects operator or end'''

    left = None
    opr = None
    uni_opr = None
    expr = None
    mode = 'n'
    while True:
        token = tr.read()

        if isinstance(token, BaseNumber) or token == '(' or token.isdigit():
            # read an operand
            if mode != 'n':
                raise ValueError('Invalid token <%s>: %s' % 
                                    (token, tr.unparsed()))

            if isinstance(token, BaseNumber):
                n = token
            elif token == '(':
                n = read_expr(tr, exit_at_right_p=True)
            else:
                n = Number(int(token))

            if not left:
                left = n
                mode = 'o'
                continue

            # read next token to see if it's a high precedence operator
            next_token = tr.read()
            if next_token in ('+', '-', ')', ''):
                # the operand belongs to the left operator
                tr.push(next_token)
                expr.add(n, opr != uni_opr)

                if exit_at_one_expr:
                    assert(uni_opr == '*')
                    return expr

            elif next_token in ('*', '/'):
                if uni_opr == '+':
                    # the operand belongs to the right operator
                    tr.push(next_token)
                    tr.push(n)
                    n = read_expr(tr, exit_at_one_expr=True)
                else:
                    tr.push(next_token)

                expr.add(n, opr != uni_opr)

            else:
                raise ValueError('Invalid token <%s> %s' % 
                                (next_token, tr.unparsed()))

            mode = 'x'

        elif token in ('+', '-', '*', '/'):
            if mode == 'n':
                if token == '+' and not left:
                    continue

                raise ValueError('Invalid token <%s>: %s' % 
                                (token, tr.unparsed()))

            opr = token
            uni_opr = opr2uni(opr)

            if not expr:
                # first operator of the expr
                expr = Expr(uni_opr)
                expr.add(left)

            elif expr.opr != uni_opr:
                # opr has a different precedence as the prior opr
                left = expr
                expr = Expr(uni_opr)
                expr.add(left)

            mode = 'n'

        elif token == ')':
            if exit_at_right_p and expr and mode == 'x':
                return expr

            raise ValueError('Invalid token (%s): %s' % 
                            (token, tr.unparsed()))

        else:
            # expression parsed, no more tokens
            if mode == 'x' and not exit_at_right_p:
                return expr

            elif mode == 'x':
                missed = ')'

            elif mode == 'n':
                missed = 'operand'

            elif mode == 'o':
                missed = 'operator'

            raise ValueError('Invalid expression: %s missed' % missed)


def parse(solution):
    return read_expr(TokenReader(solution))


