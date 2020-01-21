# -*- coding: utf-8 -*-


import sys
from lexer import Lexer


if __name__ == '__main__':
    l = Lexer(sys.argv[1])
    c = l.get_next_char()
    while l.current_char:
        c += l.get_next_char()

    print(c)
