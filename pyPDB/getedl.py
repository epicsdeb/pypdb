# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import re, sys
from warnings import warn

from pyPDB.dbd.expand import findFile
from pyPDB.po import POEnt


def main(opts,args,out):
    
    attrpat=re.compile('^\s* (\S+) \s* "(\\"|[^"]*)" \s*$', re.X)
    
    # widget attributes known to contain PV names
    PVattrs=[
    'alarmPv',
    'colorPv',
    'controlPv',
    'filePv',
    'indicatorPv',
    'readPv',
    'visPv',
    'xPv',
    'yPv',
    ]
    
    # Just a record name with optional field
    #   record.FLD
    plainpv=re.compile('^\s*([^.]+)\.?.*$')
    
    
    def extractRec(s):
        """ Extract record name(s) from string
        """
        
        if s.startswith('CALC'):
            # May contain several record names
            #   CALC\\\{(((A=0)&&(B=0)))\}($(P)$(M).DMOV, $(P)$(M).STAT)
    
            _,_,pvs = s.partition('\\}')
            pvs=pvs.strip().strip('()')
    
            if len(pvs)==0:
                warn('CALC with no PVs? "%s"'%s)
                return []
            
            pvs=pvs.split(',')
            pvs=map(str.strip, pvs)
            # strip field names
            pvs=map(lambda p:extractRec(p)[0],pvs)
    
            return pvs
    
        else:
            M=plainpv.match(s)
            if M is None:
                return []
            return [M.group(1)]
    
    entries={}
    
    for fname in args:
    
        try:
            fullname=findFile(fname, path=opts.include, env='EDMDATAFILES') 
    
            fd=open(fullname, 'rU')
    
        except IOError:
            sys.stderr.write("Can't find/read %s in %s\n"%(fname,', '.join(opts.include)))
            sys.exit(1)
    
        for ln, L in enumerate(fd.readlines()):
            M=attrpat.match(L)
            if M is None:
                continue
    
            if M.group(1) not in PVattrs:
                continue
            
            pvs=extractRec(M.group(2))
            pvs=list(set(pvs)) # make unique
    
            for pv in pvs:
                try:
                    ent=entries[pv]
                except KeyError:
                    ent=POEnt(pv)
                    entries[pv]=ent
    
                if M.group(1) not in ent.comExt:
                    ent.comExt.append(M.group(1))
    
                ent.refs.append('%s:%d'%(fname,ln))

        fd.close()
    
    return entries
