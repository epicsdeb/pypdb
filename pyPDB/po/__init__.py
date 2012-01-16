# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

PO (gettext) translation file generator
"""

import time

__all__ = ['POEnt','writePO']

class POEnt(object):
    ID=None  # untranslated
    STR=None # translated
    
    comTR=None  # translator's comments
    comExt=None # extracted comments
    refs=None   # Source refereneces
    flags=None
    olds=None   # Previous translations

    def __init__(self, ID=''):
        self.ID=ID
        self.STR=''
        self.comTR=[]
        self.comExt=[]
        self.refs=[]
        self.flags=[]
        self.olds=[]

    def __cmp__(self, o):
        return cmp(self.ID, o.ID)

def writePO(fd, ents, header={}):
    """Takes a file desriptor, list of POEnts, and a dictionary of
    header tags
    """
    
    header.setdefault('time',time.strftime('%F %H:%M%z'))
    header.setdefault('projid','')
    header.setdefault('lasttr','')
    header.setdefault('team','')
    header.setdefault('lang','')
    
    print >>fd,"""msgid ""
msgstr ""
"Project-Id-Version: %(projid)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: %(time)s\\n"
"Last-Translator: %(lasttr)s\\n"
"Language-Team: %(team)s\\n"
"Language: %(lang)s\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=iso-8859-1\\n"
"Content-Transfer-Encoding: 8bit\\n" """ % header
    
    path=header.get('path',[])
    if len(path)>0:
        print >>fd,'"X-Poedit-Basepath: %s\\n"'%(path[0])
    for n,d in enumerate(path):
        print >>fd,'"X-Poedit-SearchPath-%d: %s\\n"'%(n,d)
    print >>fd

    for E in ents:
        for c in E.comTR:
            print >>fd,'# ',c
        for c in E.comExt:
            print >>fd,'#.',c
        for c in E.refs:
            print >>fd,'#:',c
        for c in E.flags:
            print >>fd,'#,',c
        for c in E.olds:
            print >>fd,'#|',c
    
        print >>fd,'msgid "%s"'%E.ID
        print >>fd,'msgstr "%s"'%E.STR
        print >>fd
