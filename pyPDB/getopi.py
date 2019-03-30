# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import sys, re
from pyPDB.dbd.expand import findFile
from pyPDB.po import POEnt

import xml.parsers.expat

# tags with the PV name as data
#  ie <tag>PV.FLD</tag>

# static tag names
bodypvs=[
'pv_name', # in all widgets
'pv',      # in widget rules

# xy graph
'trigger_pv',

# intensity
'horizon_profile_x_pv_name',
'horizon_profile_y_pv_name',
'vertical_profile_x_pv_name',
'vertical_profile_y_pv_name',
]

# pattern tag names
bodypatpvs=[
# xy graph
'trace_[0-9]+_[a-zA-Z]+_pv'
]
bodypatpvs=list(map(re.compile, bodypatpvs))

class tagger(object):
    def __init__(self, db):
        self.db=db
        self.parser=None
        self.fname='<unknown>'
        self.cdata=''

    def getLoc(self):
        return '%s:%d'%(self.fname, self.parser.CurrentLineNumber)

    def addPV(self, s):
        s=s.strip()
        if s.startswith('epics://'):
            _,_,s=s.partition('epics://')
        elif s.startswith('loc://'):
            return None

        pv,_,_ = s.partition('.')

        try:
            ent=self.db[pv]
        except KeyError:
            ent=POEnt(pv)
            self.db[pv]=ent

        ent.refs.append(self.getLoc())
        return ent

    def start_element(self, name, attrs):
        pass
    
    def char_data(self, data):
        self.cdata+=data
        # pyexpact sometimes delivers charactor data in pieces

    def end_element(self, tag):
        
        data, self.cdata = self.cdata.strip(), ''

        if len(data)==0:
            return

        ent=None

        if tag in bodypvs:
            ent=self.addPV(data)

        else:
            for P in bodypatpvs:
                if P.match(tag) is not None:
                    ent=self.addPV(data)
                    break

        if ent is not None:
            if tag not in ent.comExt:
                ent.comExt.append(tag)



def main(opts,args,out):
    entries={}

    T = tagger(entries)
    
    for fname in args:
    
        try:
            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = T.start_element
            p.EndElementHandler = T.end_element
            p.CharacterDataHandler = T.char_data
            
            T.parser = p
            T.fname = fname

            fullname=findFile(fname, path=opts.include) 

            fd=open(fullname, 'rb')
            p.ParseFile(fd)
            fd.close()

        except IOError:
            sys.stderr.write("Can't find/read %s in %s\n"%(fname,', '.join(opts.include)))
            sys.exit(1)

    return entries
