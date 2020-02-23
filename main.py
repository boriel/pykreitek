# -*- coding: utf-8 -*-

import argparse
import sys
import io

from parser import Parser
import visitor


def main(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('FILENAME', type=str, help='Program name')

    options = arg_parser.parse_args(argv[1:])
    parser = Parser(options.FILENAME)
    ast_ = parser.parse_program()
    strout = io.StringIO()
    vis = visitor.Visitor(strout, ast_)
    vis.visit()
    print(strout.getvalue())

if __name__ == '__main__':
    main(sys.argv)
