# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import unittest

from .. import yacc
from ..ast import Code, Comment, Block, Command, DBSyntaxError

class TestParse(unittest.TestCase):
    data = [
        # Empty db
        ("""
        """,[
        ]),
        ("""# hello
        record(A, "B")
        record(C, "D") { one(two) {} }
        """,[
            Comment(" hello"),
            Block('record', ["A", "B"], [False, True]),
            Block('record', ["C", "D"], [False, True], body=[
                Block('one', ["two"], [False], []),
            ]),
        ]),
    ]

    def test_ast(self):
        for n,(I, E) in enumerate(self.data):
            try:
                O = yacc.parse(I)
                self.assertListEqual(E, O)
            except:
                print 'Error in case', n
                raise

class TestParseFail(unittest.TestCase):
    def test_fail(self):
        
        self.assertRaises(DBSyntaxError, yacc.parse, '"foo bar')
        self.assertRaises(DBSyntaxError, yacc.parse, '"foo \\"bar')

        self.assertRaises(DBSyntaxError, yacc.parse, 'foo {')
        self.assertRaises(DBSyntaxError, yacc.parse, '{')
        self.assertRaises(DBSyntaxError, yacc.parse, 'A { B')
        self.assertRaises(DBSyntaxError, yacc.parse, 'A { B { }')

        self.assertRaises(DBSyntaxError, yacc.parse, 'A ( B ')
        self.assertRaises(DBSyntaxError, yacc.parse, 'A ( B, ')

    def test_msg(self):
        self.assertRaisesRegexp(DBSyntaxError, "Missing closing quote",
                                yacc.parse, '"foo bar\n')

        self.assertRaisesRegexp(DBSyntaxError, "Missing closing quote",
                                yacc.parse, '"foo\nbar')

        self.assertRaisesRegexp(DBSyntaxError, "Missing closing quote",
                                yacc.parse, '"foo bar')

        self.assertRaisesRegexp(DBSyntaxError, "Syntax error at {",
                                yacc.parse, 'for(a {}')
