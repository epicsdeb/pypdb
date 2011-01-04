#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, sys, os.path
from warnings import warn
from optparse import OptionParser

from pyPDB.po.grammer import PO

parser = OptionParser(usage='%prog [options] <-i file.po ...> <input.db | in.edl>')
parser.add_option('-i', '--po', action='append', default=[],
                  help='Translation file(s) to apply', metavar='FILE')
parser.add_option('-o', '--output', default='.',
                  help='Location to write output files', metavar='DIR')
parser.add_option('-R', '--reverse', action='store_true', default=False,
                  help='Apply reverse translation')

opts, args = parser.parse_args()

if len(opts.po)==0:
    parser.error('No translation files specified')

mappings={}
src={}

def loadPO(file):
    x=PO.parseFile(file)

    for orig, sub in x:
        if len(orig.strip())==0 or len(sub.strip())==0:
            continue
        if orig in mappings:
            if mappings[orig] != sub:
                warn("Found duplicate definition of '%s'\nIn '%s'\nPrevious '%s'"% \
                        (orig, file, src[orig]))
            else:
                pass # duplicate, but idential

        else: # new mapping
            mappings[orig]=sub
            src[orig]=file

for po in opts.po:
    loadPO(po)

if opts.reverse:
    fail=False
    nm={}
    for orig, sub in mappings.iteritems():
        if sub not in nm:
            nm[sub]=orig

        else:
            print >>sys.stderr,"""Un-reversable mapping
From %(origfile)s '%(orig)s = %(sub)s'
and
From %(prevfile)s '%(prev)s = %(sub)s'
""" % {'orig':orig, 'sub':sub, 'prev':nm[sub],
       'origfile':src[orig], 'prevfile':src[nm[sub]]}
            fail=True
    if fail:
        sys.exit(1)
    mappings=nm

#valid   = PP.alphanums + '$:-[]{}<>()'

actions=[]

for orig, sub in mappings.iteritems():
    # look behind for beginning of line or a non-name charactor
    # look ahead for end of line or a non-name charactor
    tst = '(?:^|(?<=[\s."]))' + re.escape(orig) + '(?:$|(?=[\s."]))'
    actions.append((re.compile(tst), sub))

for f in args:
    out=os.path.join(opts.output, os.path.basename(f))

    inp=open(f, 'rU')
    val=inp.read()

    for pat, sub in actions:
        val=pat.sub(sub, val)

    out=open(out, 'wb')
    for L in val.splitlines():
        out.write(L+inp.newlines)

    out.close()
    inp.close()
