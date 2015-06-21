# -*- coding: utf-8 -*-
"""
DB/DBD lexer
"""

import logging
_log = logging.getLogger(__name__)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)

from ply import lex

from .ast import unescape, Comment, Code, DBSyntaxError

try:
    from . import lextab
except:
    _log.warn('Unable to load lextab')
    lextab = None

tokens = (
    'BARE',
    'QUOTED',
    'COMMENT',
    'CODE',
)

literals = (',', '{', '}', '(', ')')

t_ignore = ' \t'

def t_QUOTED(t):
    r'"(?:\\.|[^"])*"'
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
    r'"(?:\\.|[^"])*\n'
    raise DBSyntaxError('Missing closing quote on line %d'%t.lexer.lineno)

def t_error(t):
    raise DBSyntaxError("illegal char '%s' on line %d"%(t.value, t.lexer.lineno))

if __name__=='__main__':
    lexer = lex.lex(debug=1, optimize=1, lextab=lextab, debuglog=_log)
    lex.runmain(lexer=lexer)
