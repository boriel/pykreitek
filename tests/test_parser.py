# -*- coding: utf-8 -*-

import io
import parser


def test_parser_init():
    parser_ = parser.Parser(io.StringIO(''))


