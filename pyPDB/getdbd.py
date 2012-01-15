# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
mrfioc2 is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

from warnings import warn
from collections import defaultdict
    
from pyPDB.po import POEnt
from pyPDB.dbd.expand import loadDBD, DBD

linktypes = ['DBF_INLINK', 'DBF_OUTLINK', 'DBF_FWDLINK']
infofields = ['EGU', 'DESC']

def main(opts,args,out):
    
    pdb=[]
    
    pcache=defaultdict(dict)
    
    for inp in args:
        pdb+=loadDBD(inp, path=opts.include, cache=pcache)
    
    pdb=DBD(pdb)
    
    pdb.singular('recordtype')
    if not opts.dups:
        pdb.singular('record')
    
    def cleanLink(val):
        val=val.strip()
        v,_,_=val.partition('.')
        v,_,_=v.partition(' ')
        return v.strip()
    
    # list of translatable fields by recordtype
    recflds={}
    
    entries={}
    
    def allentries(sec):
        for s in sec:
            assert isinstance(s, list)
            for inst in s:
                yield inst
    
    if opts.dups:
        I=allentries(pdb.records.itervalues())
    else:
        I=pdb.records.itervalues()
    
    for rec in I:
        #print rec,flds[0],
    
        try:
            ent = entries[rec.name]
        except KeyError:
            ent = POEnt(rec.name)
            entries[rec.name] = ent
    
        # prepend definition(s)
        ent.comExt.insert(0, 'recordtype: %s'%rec.rec)
        ent.refs.insert(0, '%s:%d'%(rec.name.file, rec.name.lineno))
    
        rtype=pdb.recordtypes.get(rec.rec, None)
        if rtype is None:
            warn("%s : Skipping unknown recordtype '%s'"%(rec.name,rec.rec))
            continue
    
        interesting=recflds.get(rtype,  None)
        if interesting is None:
            interesting=[]
            for rf in rtype.fields:
                if rf.dbf in linktypes:
                    interesting.append(rf.name)
            recflds[rtype]=interesting
    
        for fld in rec.fields:
            if fld.name in interesting:
                #print fld.name,
                try:
                    float(fld.value)
                    # Constant link
                    continue
                except ValueError:
                    pass
                
                val=cleanLink(fld.value)
    
                if len(val)==0 or val[0]=='@':
                    continue
        
                try:
                    valent=entries[val]
                except KeyError:
                    valent=POEnt(val)
                    entries[val] = valent
                
                valent.refs.append('%s:%d'%(fld.value.file, fld.value.lineno))
     
            if fld.name in infofields:
                ent.comExt.append('%s: %s'% \
                    (fld.name, repr(fld.value)[1:-1]))
    
        #print
    
    return entries
