# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.

PO (gettext) translation file generator
"""

import time
from functools import total_ordering

__all__ = ['POEnt','writePO']

@total_ordering
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

    def __lt__(self, o):
        return self.ID < o.ID

def writePO(fd, ents, header={}):
    """Takes a file desriptor, list of POEnts, and a dictionary of
    header tags
    """
    
    header.setdefault('time',time.strftime('%F %H:%M%z'))
    header.setdefault('projid','')
    header.setdefault('lasttr','')
    header.setdefault('team','')
    header.setdefault('lang','')
    
    fd.write("""msgid ""
msgstr ""
"Project-Id-Version: %(projid)s\\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: %(time)s\\n"
"Last-Translator: %(lasttr)s\\n"
"Language-Team: %(team)s\\n"
"Language: %(lang)s\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=iso-8859-1\\n"
"Content-Transfer-Encoding: 8bit\\n" 
"X-Generator: pyPDB\\n"
""" % header)
    
    path=header.get('path',[])
    if len(path)>0:
        fd.write('"X-Poedit-Basepath: %s\\n"\n'%(path[0]))
    for n,d in enumerate(path):
        fd.write('"X-Poedit-SearchPath-%d: %s\\n"\n'%(n,d))
    fd.write("\n")

    for E in ents:
        for c in E.comTR:
            fd.write('# %s\n'%c)
        for c in E.comExt:
            fd.write('#. %s\n'%c)
        for c in E.refs:
            fd.write('#: %s\n'%c)
        for c in E.flags:
            fd.write('#, %s\n'%c)
        for c in E.olds:
            fd.write('#| %s\n'%c)
    
        fd.write('msgid "%s"\n'%E.ID)
        fd.write('msgstr "%s"\n'%E.STR)
        fd.write("\n")
