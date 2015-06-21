# -*- coding: utf-8 -*-
"""
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
            print >>fd,'%s%s %s'%(indent, ent.name, A)

        elif isinstance(ent, Block):
            As = []
            for A,Q in zip(ent.args, ent.argsquoted):
                if Q:
                    As.append(quote(A))
                else:
                    As.append(A)

            print >>fd,"%s%s(%s)"%(indent, ent.name, ', '.join(As)),

            if ent.name=='breaktable':
                print >>fd

            elif ent.body is None:
                print >>fd

            else:
                print >>fd,"%s{"%indent
                showDBD(ent.body, fd, indent+'  ')
                print >>fd,"%s}"%indent

        elif isinstance(ent, Comment):
            print >>fd,"%s#%s"%(indent, ent.value)

        elif isinstance(ent, Code):
            print >>fd,"%s%%%s"%(indent, ent.value)

        else:
            warnings.warn("Unknown entry '%s' (%s)"%(ent,type(ent)))
