# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

from warnings import warn
    
from pyPDB.po import POEnt
from pyPDB.dbd.expand import loadDBD, DBD

from .dbd.ast import Block

linktypes = ['DBF_INLINK', 'DBF_OUTLINK', 'DBF_FWDLINK']
infofields = ['EGU', 'DESC']

def main(opts,args,out):
    
    pdb=[]
    
    pcache={}
    
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
        I=allentries(pdb.records.values())
    else:
        I=pdb.records.values()
    
    for rec in I:
    
        try:
            ent = entries[rec.args[1]]
        except KeyError:
            ent = POEnt(rec.args[1])
            entries[rec.args[1]] = ent
    
        # prepend definition(s)
        ent.comExt.insert(0, 'recordtype: %s'%rec.args[0])
        ent.refs.insert(0, '%s:%d'%(rec.fname, rec.lineno))
    
        rtype=pdb.recordtypes.get(rec.args[0], None)
        if rtype is None:
            warn("%s : Skipping unknown recordtype '%s'"%(rec.name,rec.args[0]))
            continue
    
        interesting=recflds.get(rec.args[0],  None)
        if interesting is None:
            interesting=[]
            for rf in rtype.body:
                if not isinstance(rf, Block) or rf.name!='field':
                    continue
                if rf.args[1] in linktypes:
                    interesting.append(rf.args[0])
            recflds[rec.args[0]]=interesting
    
        for fld in rec.body:
            if not isinstance(fld, Block) or fld.name!='field':
                continue
            if fld.args[0] in interesting:
                try:
                    float(fld.args[1])
                    # Constant link
                    continue
                except ValueError:
                    pass
                
                val=cleanLink(fld.args[1])
    
                if len(val)==0 or val[0]=='@':
                    continue
        
                try:
                    valent=entries[val]
                except KeyError:
                    valent=POEnt(val)
                    entries[val] = valent
                
                valent.refs.append('%s:%d'%(fld.fname, fld.lineno))
     
            if fld.name in infofields:
                ent.comExt.append('%s: %s'% \
                    (fld.name, repr(fld.value)[1:-1]))
    
        #print
    
    return entries
