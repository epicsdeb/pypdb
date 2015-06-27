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
    'MACRO',
)

states = (
    ('macro', 'exclusive'),
)

literals = (',', '{', '}', '(', ')', '=')

t_ignore = ' \t\r'

t_macro_ignore = '' # don't ignore whitespace

def t_QUOTED(t):
    r'"(?:\\.|[^"\n])*"'
    t.value = t.value[1:-1]
    if t.value.find('\\')!=-1:
        t.value = unescape(t.value)
    return t

t_BARE = r'[a-zA-Z0-9_+:.\[\]<>;-]+'

_mac = {'{':'}', '(':')'}

def t_startmac(t):
    r'\$[{(]'
    t.lexer._mval = [t.value]
    t.lexer._mdepth = [_mac[t.value[-1]]]
    t.lexer.push_state('macro')
    # don't emit token

def t_macro_value(t):
    r'[^$(){}]+'
    t.lexer._mval.append(t.value)

def t_macro_recurse(t):
    r'\$[{(]'
    t.lexer._mval.append(t.value)
    t.lexer._mdepth.append(_mac[t.value[-1]])

def t_macro_return(t):
    r'[})]'
    if t.value!=t.lexer._mdepth[-1]:
        P = t.lexer.lexpos
        raise lex.LexError("Mis-matched bracket when closing macro",
                           t.lexer.lexdata[P:P:20])
    else:
        t.lexer._mval.append(t.value)
        t.lexer._mdepth.pop()
        if len(t.lexer._mdepth)==0:
            t.type = 'MACRO'
            t.value = ''.join(t.lexer._mval)
            del t.lexer._mval
            del t.lexer._mdepth
            t.lexer.pop_state()
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

def t_quotedunterm(t):
    r'"(?:\\.|[^"\n])*\n'
    raise DBSyntaxError('Missing closing quote on line %d'%t.lexer.lineno)

def t_quotedeol(t):
    r'"(?:\\.|[^"\n])*\Z'
    raise DBSyntaxError('Missing closing quote at end of file')

def t_error(t):
    raise DBSyntaxError("illegal char '%s' (state %s)"%(t.value[0],t.lexer.current_state()),
                        getattr(t.lexer, '_file'), t.lexer.lineno)

t_macro_error = t_error

def main():
    import logging
    lexer = lex.lex(debug=1, optimize=0, debuglog=logging.getLogger(__name__))
    lexer._file = '<???>'
    lex.runmain(lexer=lexer)
    if lex.lexer.current_state()!='INITIAL':
        raise DBSyntaxError("open macro at EOF", lexer._file, -1)

if __name__=='__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    main()
