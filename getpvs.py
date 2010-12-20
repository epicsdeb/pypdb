#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from warnings import warn
from optparse import OptionParser
from collections import defaultdict

from pyPDB.dbd.expand import loadDBD, DBD

linktypes = ['DBF_INLINK', 'DBF_OUTLINK', 'DBF_FWDLINK']

parser = OptionParser()
parser.add_option("-I", dest='include', action='append', default=[],
                  help='Add to search path', metavar='PATH')
parser.add_option("-o", '--output',
                  help='Output file', metavar='FILE')
parser.add_option('-M', '--merge-duplicates', dest='dups', action='store_true',
                  help='When encountering records with duplicate names '
                  'treat them as one record')

opts, args = parser.parse_args()

if opts.output is None:
    import sys
    out=sys.stdout
else:
    out=file(opts.output, 'w')

#from dbd.grammer import DBD
#DBD.setDebug(True)

pdb=[]

for inp in args:
    pdb+=loadDBD(inp, path=opts.include)

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

strings=defaultdict(list)
comments={}

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

    # prepend definition(s)
    strings[rec.name].insert(0, '%s:%d'%(rec.name.file, rec.name.lineno))

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
 
            if val not in strings:
                strings[val]=[]

            strings[val].append('%s:%d'%(fld.value.file, fld.value.lineno))

        if fld.name=='DESC':
            comments[rec]=fld.value

    #print

print >>out,"""msgid ""
msgstr ""
"Project-Id-Version: \\n"
"POT-Creation-Date: %(time)s\\n"
"PO-Revision-Date: %(time)s\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=iso-8859-1\\n"
"Content-Transfer-Encoding: 8bit\\n" """ % {'time':time.strftime('%F %H:%M%z')}

for n,d in enumerate(opts.include):
    print >>out,'"X-Poedit-SearchPath-%d: %s\\n"'%(n,d)
print >>out

pvs=strings.items()
pvs.sort()
for pv, refs in pvs:
    if pv in comments:
        print >>out,'#.',comments[pv]
    for r in refs:
        print >>out,'#:',r
    print >>out,'msgid "%s"'%pv
    print >>out,'msgstr ""'
    print >>out
