# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

DB/DBD file parser
"""

from __future__ import print_function

import logging
_log = logging.getLogger(__name__)

from ply import yacc, lex

from . import lex as lexmod
from . import ast

from .lex import tokens

start = 'nodelist'

def p_bvalue(p):
    '''bval : BARE
            | MACRO
            | BARE bval
            | MACRO bval
            |
    '''
    L = []
    if len(p)>2:
        L = p[2]
    if len(p)>1:
        L.insert(0,p[1])
    p[0] = L

def p_value_Q(p):
    '''value : QUOTED
    '''
    p[0] = (p[1], True)

def p_value(p):
    '''value : bval
    '''
    p[0] = (' '.join(p[1]), False)

def p_nodelist_one(p):
    '''nodelist : node
    '''
    p[0] = [p[1]]

def p_nodelist_many(p):
    '''nodelist : node nodelist
    '''
    L = p[2]
    L.insert(0, p[1])
    p[0] = L

def p_nodelist_empty(p):
    '''nodelist :
    '''
    p[0] = []

def p_node(p):
    '''node : block
            | command
            | CODE
            | COMMENT
    '''
    N = p[0] = p[1]
    N.fname = p.lexer._file

def p_block_plain(p):
    '''block : BARE '(' arglist ')'
    '''
    Vs, Qs = p[3]
    p[0] = ast.Block(p[1], Vs, Qs, body=None, lineno=p.lineno(1))

def p_block_body(p):
    '''block : BARE '(' arglist ')' '{' nodelist '}'
    '''
    Vs, Qs = p[3]
    p[0] = ast.Block(p[1], Vs, Qs, body=p[6], lineno=p.lineno(1))

def p_command(p):
    '''command : BARE BARE
    '''
    p[0] = ast.Command(p[1], p[2], False, p.lineno(1))

def p_commandQ(p):
    '''command : BARE QUOTED
    '''
    p[0] = ast.Command(p[1], p[2], True, p.lineno(1))

def p_arglist_one(p):
    '''arglist : value
    '''
    V, Q = p[1]
    p[0] = [V], [Q]

def p_arglist_many(p):
    '''arglist : value ',' arglist
    '''
    V, Q = p[1]
    p[0] = LV, LQ = p[3]
    LV.insert(0, V)
    LQ.insert(0, Q)

def p_arglist_empty(p):
    '''arglist :
    '''
    p[0] = []

def p_error(t):
    if t is None:
        raise ast.DBSyntaxError("Syntax error near end of input")
    else:
        raise ast.DBSyntaxError("Syntax error at or before %s"%t.value, getattr(t.lexer,'_file'), t.lexer.lineno)

dodebug=0
if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    dodebug=1

_lexer = lex.lex(module=lexmod, debug=dodebug, optimize=0, debuglog=_log)
_parser = yacc.yacc(debug=dodebug, write_tables=0, errorlog=_log, debuglog=_log)

def parse(txt, debug=dodebug, file=None):
    """This function parses the provided text and returns
    a list of nodes (:token:`nodelist`).
    Each node is one of :class:`Block`, :class:`Command`,
    :class:`Code`, or :class:`Comment`.
    
    :param str txt: The text to be parsed
    :param bool debug: Log verbose debugging information with the logging module
    :param str file: The file name
    :return: A list of nodes
    :rtype: list
    :raises: :class:`DBSyntaxError` If parsing fails
    """
    L = _lexer.clone()
    L._file = file
    try:
        return _parser.parse(txt, lexer=L, debug=debug)
        if L.lexer.current_state()!='INITIAL':
            raise ast.DBSyntaxError("open macro at EOF", file, L.lineno)
    except ast.DBSyntaxError as e:
        e.fname = file
        if e.lineno is None:
            e.lineno = L.lineno
        raise

if __name__=='__main__':
    import sys
    try:
        fname = sys.argv[1]
        with open(sys.argv[1],'r') as F:
            data = F.read()
    except:
        fname = '<stdin>'
        data = sys.stdin.read()

    print('Start')
    V = parse(data, debug=1, file=fname)

    import pprint
    pprint.pprint(V)
