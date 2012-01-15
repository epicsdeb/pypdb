# -*- coding: utf-8 -*-

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
'trace_[0-9]+_[a-z]_pv'
]
bodypatpvs=map(re.compile, bodypatpvs)

class tagger(object):
    def __init__(self, db):
        self.stack=[]
        self.db=db
        self.parser=None
        self.fname='<unknown>'

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
        self.stack.append(name)
    
    def char_data(self, data):
        tag=self.stack[-1]
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


    def end_element(self, name):
        self.stack.pop()

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
            print fullname
            fd=open(fullname, 'rU')
            p.ParseFile(fd)
            fd.close()

        except IOError:
            print >>sys.stderr, "Can't find/read",fname,"in",', '.join(opts.include)
            sys.exit(1)

    return entries
