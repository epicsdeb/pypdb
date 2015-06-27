# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

DB/DBD file parser
"""

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
    L.insert(0,p[1])
    p[0] = L

def p_value_Q(p):
    '''value : QUOTED
    '''
    p[0] = (p[1], True)

def p_value(p):
    '''value : bval
    '''
    p[0] = (''.join(p[1]), False)

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
    p[1].fname = p.lexer._file
    p[0] = p[1]

def p_block_plain(p):
    '''block : BARE '(' arglist ')'
    '''
    Vs, Qs = [], []
    for V, Q in p[3]:
        Vs.append(V)
        Qs.append(Q)
    p[0] = ast.Block(p[1], Vs, Qs, body=None, lineno=p.lineno(1))

def p_block_body(p):
    '''block : BARE '(' arglist ')' '{' nodelist '}'
    '''
    Vs, Qs = [], []
    for V, Q in p[3]:
        Vs.append(V)
        Qs.append(Q)
    p[0] = ast.Block(p[1], Vs, Qs, body=p[6], lineno=p.lineno(1))

def p_command(p):
    '''command : BARE value
    '''
    V, Q = p[2]
    p[0] = ast.Command(p[1], V, Q, p.lineno(1))

def p_arglist_one(p):
    '''arglist : value
    '''
    p[0] = [p[1]]

def p_arglist_many(p):
    '''arglist : value ',' arglist
    '''
    L = p[3]
    L.insert(0, p[1])
    p[0] = L

def p_arglist_empty(p):
    '''arglist :
    '''
    p[0] = []

def p_error(t):
    if t is None:
        raise ast.DBSyntaxError("Syntax error at end of input")
    else:
        raise ast.DBSyntaxError("Syntax error at %s"%t.value, getattr(t.lexer,'_file'), t.lexer.lineno)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)

_lexer = lex.lex(module=lexmod, debug=0, optimize=0, debuglog=_log)
_parser = yacc.yacc(debug=0, write_tables=0, errorlog=_log, debuglog=_log)

def parse(txt, debug=0, file=None):
    L = _lexer.clone()
    L._file = file
    try:
        return _parser.parse(txt, lexer=L, debug=debug)
        if L.lexer.current_state()!='INITIAL':
            raise ast.DBSyntaxError("open macro at EOF", file, L.lineno)
    except ast.DBSyntaxError as e:
        e.fname = file
        raise

if __name__=='__main__':
    import sys
    try:
        with open(sys.argv[1],'r') as F:
            data = F.read()
    except:
        data = sys.stdin.read()

    print 'Start'
    V = parse(data, debug=1)

    import pprint
    pprint.pprint(V)
