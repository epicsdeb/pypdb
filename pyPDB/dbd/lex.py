# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

DB/DBD file lexer
"""

from ply import lex

from .ast import unescape, Comment, Code, DBSyntaxError

tokens = (
    'BARE',
    'QUOTED',
    'COMMENT',
    'CODE',
)

literals = (',', '{', '}', '(', ')')

t_ignore = ' \t'

def t_QUOTED(t):
    r'"(?:\\.|[^"\n])*"'
    t.value = t.value[1:-1]
    if t.value.find('\\')!=-1:
        t.value = unescape(t.value)
    return t

def t_BARE(t):
    r'[^"\\#% \t\r\n(){},]+'
    return t

def t_COMMENT(t):
    r'\#[^\n]*\n'
    t.value = Comment(t.value[1:-1], t.lexer.lineno)
    t.lexer.lineno += 1
    return t

def t_CODE(t):
    r'\%[^\n]*\n'
    t.value = Code(t.value[1:-1], t.lexer.lineno)
    t.lexer.lineno += 1
    return t

def t_eol(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_quoted_unterm(t):
    r'"(?:\\.|[^"\n])*\n'
    raise DBSyntaxError('Missing closing quote on line %d'%t.lexer.lineno)

def t_quoted_eol(t):
    r'"(?:\\.|[^"\n])*\Z'
    raise DBSyntaxError('Missing closing quote at end of file')

def t_error(t):
    raise DBSyntaxError("illegal char '%s'"%t.value, getattr(t.lexer, '_file'), t.lexer.lineno)

if __name__=='__main__':
    lexer = lex.lex(debug=1, optimize=0)
    lex.runmain(lexer=lexer)
