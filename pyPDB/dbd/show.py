# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
mrfioc2 is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import warnings
import sys

def showDBD(dbd, fd=sys.stdout):
    for ent in dbd:
        t=ent.what
        if t=='include':
            print >>fd,'include "%s"'%ent.name

        elif t=='menu':
            print >>fd,'menu(%s) {'%ent.name
            for k,v in ent.choices.iteritems():
                print >>fd,'    choice(%s,"%s")'%(k,v)
            print >>fd,'}'

        elif t=='record':
            print >>fd,'record(%s,"%s") {'%(ent.rec, ent.name)
            for f in ent.fields:
                if f.what=='include':
                    print >>fd,'    include "%s"'%f.name

                elif f.what in ['field', 'info']:
                    print >>fd,'    %s(%s, "%s")'%(f.what,f.name,f.value)

                elif f.what=='alias':
                    print >>fd,'    alias("%s")'%(f.name)

                else:
                    warnings.warn("Unknown entry '%s' in record %s"%\
                                (f.what, ent.name))

            print >>fd,'}'

        elif t=='recordtype':
            print >>fd,'recordtype(%s) {'%ent.name
            for f in ent.fields:
                if f.what=='include':
                    print >>fd,'    include "%s"'%f.name

                elif f.what=='field':
                    print >>fd,'\tfield(%s,%s) {'%(f.name,f.dbf)

                    for k,v in f.attrs.iteritems():
                        if k in ['prompt', 'initial', 'extra']:
                            print >>fd,'\t\t%s("%s")'%(k,v)
                        else:
                            print >>fd,'\t\t%s(%s)'%(k,v)

                    print >>fd,'\t}'

                elif f.what=='CCode':
                    print >>fd,'    %%%s'%f.code

                else:
                    warnings.warn("Unknown entry '%s' in recordtype %s"%\
                                (f.what, ent.name))
            print >>fd,'}'

        elif t=='breaktable':
            print >>fd, 'breaktable(%s) {' % ent.name
            for E in ent.table:
                print >>fd, '    %.06f %.06f'%tuple(E)
            print >>fd, "}"

        elif t=='device':
            print >>fd,'device(%s,%s,%s,"%s")' % (ent.rec, ent.link, ent.name, ent.dtyp)

        elif t=='variable':
            print >>fd,'variable(%s,%s)' % (ent.name,ent.ctype)

        elif t=='registrar':
            print >>fd,'registrar(%s)' % ent.name

        else:
            warnings.warn("Unknown entry '%s'"%\
                        (ent.what))
