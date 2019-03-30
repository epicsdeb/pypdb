# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import warnings
import sys

from .ast import Block, Command, Comment, Code, quote

def showDBD(dbd, fd=sys.stdout, indent=''):
    for ent in dbd:
        if isinstance(ent, Command):
            A = ent.arg
            if ent.argquote:
                A = quote(A)
            fd.write('%s%s %s\n'%(indent, ent.name, A))

        elif isinstance(ent, Block):
            As = []
            for A,Q in zip(ent.args, ent.argsquoted):
                if Q:
                    As.append(quote(A))
                else:
                    As.append(A)

            fd.write("%s%s(%s)\n"%(indent, ent.name, ', '.join(As))),

            if ent.name=='breaktable':
                fd.write('\n')

            elif ent.body is None:
                fd.write('\n')

            else:
                fd.write("%s{\n"%indent)
                showDBD(ent.body, fd, indent+'  ')
                fd.write("%s}\n"%indent)

        elif isinstance(ent, Comment):
            fd.write("%s#%s\n"%(indent, ent.value))

        elif isinstance(ent, Code):
            fd.write("%s%%%s\n"%(indent, ent.value))

        else:
            warnings.warn("Unknown entry '%s' (%s)"%(ent,type(ent)))
