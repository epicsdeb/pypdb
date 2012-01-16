# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

Grammer for PO (gettext) translation files
"""

from pyparsing import *

def stop(s, loc, expr, err):
    raise ParseFatalException('On %(ln)d Error: %(msg)s\n%(line)s\n%(col)s\n' % \
        {'msg':err, 'ln':lineno(loc,s), 'line':line(loc,s), 'col':(col(loc,s)-1)*'-'+'^'})

Comment = pythonStyleComment | QuotedString('"')
Comment=Comment.suppress()

MsgID = Keyword("msgid").suppress() + QuotedString('"')

MsgStr = Keyword("msgstr").suppress() + QuotedString('"')

PO = ZeroOrMore( Group( MsgID + MsgStr ) | Comment )
