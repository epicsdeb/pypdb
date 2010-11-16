# -*- coding: utf-8 -*-
"""Grammer for EPICS database
"""

from pyparsing import *

# General

_annoated={}

def annotate(s,loc,toks):
    out=[]
    for t in toks:
        cls=_annoated.get(t.__class__)
        if cls is None:
            class Annotated(t.__class__):
                file=None
                lineno=None
                col=None
            _annoated[t.__class__]=Annotated
            cls=Annotated
        tt=cls(t)
        tt.lineno=lineno(loc,s)
        tt.col=col(loc,s)
        out.append(tt)
    return out

def listToDict(toks):
    return dict(toks.asList())

upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

fldname = upper + '0123456789'

LPAREN = Suppress("(")
RPAREN = Suppress(")")
LCURL  = Suppress("{")
RCURL  = Suppress("}")
COMMA  = Suppress(",")
RECORD = (Keyword("record") | Keyword("grecord")).setName("record")

# a word with a macro
ValueWord = OneOrMore( CharsNotIn(' \t\r\n()') |
                       QuotedString('(', endQuoteChar=')',
                                         unquoteResults=False)
                     ).setName('Value Word')

UnQuotedString = Optional( ValueWord + 
                           ZeroOrMore( White(' \t') +
                                       ValueWord
                           )
                         ).setName("Un-quoted string")

DBValue = QuotedString('"', unquoteResults=True) | \
          Combine(UnQuotedString)
DBValue=DBValue.addParseAction(annotate).setName("DB Value")

Comment = pythonStyleComment

Include = Keyword("include").setResultsName('what') + \
          QuotedString('"').setResultsName('name')

#TODO: Don't work for CPP because Comment is applied
CCode = Literal("%").setParseAction(lambda _:'CCode').setResultsName('what') + \
        restOfLine.setResultsName('code')

# Menues

MenuHead = Keyword("menu").setResultsName('what') + \
                      LPAREN + \
                      Word(alphanums).setResultsName('name') + \
                      RPAREN

MenuEntry = Keyword("choice").suppress() + \
             LPAREN + \
		     Word(alphanums+'_') + \
		     COMMA + \
		     QuotedString('"') + \
		     RPAREN
MenuEntry = Group(MenuEntry)

Menu = MenuHead + LCURL + \
	      OneOrMore( MenuEntry ).setResultsName('choices').setParseAction(listToDict) + \
	      RCURL

# Records

RecordHead = Keyword("recordtype").setResultsName('what') + \
                      LPAREN + \
                      Word(alphanums).setResultsName('name') + \
                      RPAREN
RecordHead.setName("Record header")

# Record body statements

RecordFieldHead = Keyword("field").setResultsName('what') + LPAREN + \
                  Word(fldname).setResultsName('name') + COMMA + \
                  Word(upper+'_').setResultsName('dbf') + RPAREN

_valQuoted = ['prompt', 'initial', 'extra']
_valPlain = ['asl','promptgroup','special','pp',
             'interest','base','size','menu']

_fieldAttrs=[]
for v in _valQuoted:
    a=Keyword(v) + LPAREN + QuotedString('"') + RPAREN
    _fieldAttrs.append(a)

for v in _valPlain:
    a=Keyword(v) + LPAREN + Word(alphanums+'_') + RPAREN
    _fieldAttrs.append(a)

RecordFieldAttr = reduce(lambda a,b:a|b, _fieldAttrs)

RecordField = RecordFieldHead + LCURL + \
          OneOrMore( Group(RecordFieldAttr) ).setParseAction(listToDict).setResultsName('attrs') + \
          RCURL

RecordEntry = Group( RecordField | Include | CCode )

Record = RecordHead + LCURL + \
          Group( OneOrMore( RecordEntry ) ).setResultsName('fields') + \
          RCURL

# Record Instances

InstHead = RECORD.setResultsName('what') + LPAREN + \
                  Word(alphanums).setResultsName('rec') + COMMA + \
                  DBValue.setResultsName('name') + RPAREN

InstField = Keyword("field").setResultsName('what') + LPAREN + \
                  Word(fldname).setResultsName('name') + COMMA + \
                  DBValue.setResultsName('value') + RPAREN

InstInfo = Keyword("info").setResultsName('what') + LPAREN + \
                  Word(alphanums+'_').setResultsName('name') + COMMA + \
                  QuotedString('"').setResultsName('value') + RPAREN

InstAlias = Keyword("alias").setResultsName('what') + LPAREN + \
                  QuotedString('"').setResultsName('name') + RPAREN

InstEntry = Group( InstField | InstInfo | InstAlias | Include )

Inst = InstHead + LCURL + \
          Group( ZeroOrMore( InstEntry ) ).setResultsName('fields') + \
          RCURL

# misc

Registrar = Keyword('registrar') + LPAREN + \
            Word(alphanums+'_').setResultsName('name') + RPAREN

Variable = Keyword("variable").setResultsName('what') + LPAREN + \
           Word(alphanums+'_').setResultsName('name') + COMMA + \
           Word(alphanums+'_').setResultsName('ctype') + RPAREN

Device = Keyword("device").setResultsName('what') + LPAREN + \
         Word(alphanums+'_').setResultsName('rec') + COMMA + \
         Word(upper+'_').setResultsName('link') + COMMA + \
         Word(alphanums+'_').setResultsName('name') + COMMA + \
         QuotedString('"').setResultsName('dtyp') + RPAREN

# Root nodes

DBD = OneOrMore( Group(Record   | Menu   | Inst  | Registrar | \
                       Variable | Device | CCode | Include) )
DBD.ignore(Comment)

# include from recordtype
RecordInclude = OneOrMore( RecordEntry )
RecordInclude.ignore(Comment)

# include from recordtype
InstInclude = OneOrMore( InstEntry )
InstInclude.ignore(Comment)
