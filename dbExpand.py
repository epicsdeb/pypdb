#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser

from pyPDB.dbd.expand import loadDBD
from pyPDB.dbd.show import showDBD

parser = OptionParser()
parser.add_option("-I", dest='include', action='append', default=[],
                  help='Add to search path', metavar='PATH')
parser.add_option("-o", '--output',
                  help='Output file', metavar='FILE')

opts, args = parser.parse_args()

if opts.output is None:
    import sys
    out=sys.stdout
else:
    out=file(opts.output, 'w')

dbd=[]

#from dbd import grammer
#grammer.Record.setDebug(True)

for inp in args:
    dbd+=loadDBD(inp, path=opts.include)

showDBD(dbd, out)

if opts.output is not None:
    out.close()
