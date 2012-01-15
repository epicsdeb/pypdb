# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
mrfioc2 is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import sys
import warnings

from pyparsing import ParseBaseException
from collections import defaultdict
from StringIO import StringIO

import grammer

class RecursiveError(RuntimeError):
    pass

def findFile(name, path=['.'], env=None, all=False, sep=':'):
    """Search for a file with the given path
    
    Search path is argument 'path' then ENV (if given)
    If 'all' is set then return a list of all matching files,
    else just the first (or raises IOError)
    """
    from os.path import join, isfile
    from os import environ
    ret=[] # used only if all==True

    # build search path
    if env is not None and env in environ:
        opt=environ[env].split(sep)
        opt=map(str.strip, opt)

        path+=opt

    for p in path:
        if p=='':
            continue
        f=join(p,name)
        if not isfile(f):
            continue

        if all:
            ret.append(f)
        else:
            return f

    if all:
        return ret
    else:
        raise IOError(name+" not in path")

def loadEntry(name, entry, path=['.'], skip=[], cache=None):
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)

    try:
        return cache[entry][f]
    except KeyError:
        pass

    try:
        dbd=entry.parseFile(f)

        out=[]
        while len(dbd)>0:
            ent=dbd.pop(0)

            if ent.what=='include':
                R=loadEntry(ent.name, entry, path=path, skip=skip)
                out+=R                        

            elif ent.what=='field' and 'value' in ent:
                # instance field
                ent.value.file=name
                out.append(ent)
            else:
                out.append(ent)

        dbd=out
    except RecursiveError,e:
        # Append message while preserving stack trace
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nFrom %s'%(e,f))
        raise RecursiveError, next, tb

    except ParseBaseException,e:
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nOn %d (col %d) of %s\n  %s\n  %s'% \
                            (e, e.lineno, e.col, f, e.line, ('-'*(e.col-1)+'^')))
        raise RecursiveError, next, tb

    skip.pop()
    cache[entry][f]=dbd
    return dbd

class _Result(object):
    __list=None
    def __init__(self, *names):
        self.__list=names
    def __getitem__(self, key):
        return getattr(self, self.__list[key])
    def __setitem__(self, key, value):
        return setattr(self, self.__list[key], value)
    #del __delitem__(self, key):
        #return delattr(self, self.__list[key])

def loadDBD(name, path=['.'], skip=[], cache=defaultdict(dict)):
    """Recursively read and parse database
    """
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)
    
    try:
        return cache[grammer.DBD][f]
    except KeyError:
        pass

    try:
        dbd=grammer.DBD.parseFile(f)

        out=[]
        while len(dbd)>0:
            ent=dbd.pop(0)

            if ent.what=='include':
                R=loadDBD(ent.name, path=path, skip=skip)
                out+=R

            elif ent.what=='recordtype':
                nf=[]
                for fld in ent.fields:
                    if fld.what=='include':
                        R=loadEntry(fld.name, grammer.RecordInclude,
                                    path=path, skip=skip, cache=cache)
                        nf+=R

                    else:
                        nf.append(fld)

                ent2=_Result('what','name','fields')
                for n in ['what','name']:
                    setattr(ent2, n, getattr(ent, n))
                ent2.fields=nf

                out.append(ent2)

            elif ent.what=='record' or ent.what=='grecord':
                nf=[]
                ent.name.file=name
                while len(ent.fields)>0:
                    fld=ent.fields.pop(0)
                    if fld.what=='include':
                        R=loadEntry(fld.name, grammer.InstInclude,
                                    path=path, skip=skip, cache=cache)
                        nf+=R

                    elif fld.what=='field':
                        fld.value.file=name
                        nf.append(fld)

                    else:
                        nf.append(fld)

                ent2=_Result('what','rec','name','fields')
                for n in ['what','rec','name']:
                    setattr(ent2, n, getattr(ent, n))
                ent2.fields=nf

                out.append(ent2)

            else:
                out.append(ent)

        dbd=out
    except RecursiveError,e:
        # Append message while preserving stack trace
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nFrom %s'%(e,f))
        raise RecursiveError, next, tb

    except ParseBaseException,e:
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nOn %d (col %d) of %s\n  %s\n  %s'% \
                            (e, e.lineno, e.col, f, e.line, ('-'*(e.col-1)+'^')))
        raise RecursiveError, next, tb

    skip.pop()
    cache[grammer.DBD][f]=dbd
    return dbd

class DBD(object):
    def __init__(self, dbd=None):
        self.recordtypes=defaultdict(list)
        self.menus=defaultdict(list)
        self.records=defaultdict(list)
        self._dispatch={'menu':self.menus,
                        'record':self.records,
                        'grecord':self.records,
                        'recordtype':self.recordtypes}
        if dbd is not None:
            self.load(dbd)

    def load(self, dbd):
        # group by type
        for ent in dbd:
            d=self._dispatch.get(ent.what, None)
            if d is None:
                continue
            d[ent.name].append(ent)

    def singular(self, type):
        """Enforce that entries of 'type' have unique names
        """
        d=self._dispatch[type]
        n=defaultdict(list)
        R=StringIO()
        for name, ent in d.iteritems():
            if len(ent)>1:
                print >>R,'\nDuplicate definitions for %s \'%s\''% \
                  (type,name)
                for inst in ent:
                    print >>R,'  %s:%d'%(inst.name.file, inst.name.lineno)
            n[name]=ent[0]
        R.seek(0)
        R=R.read()
        if len(R)>0:
            print R
            raise KeyError('duplicate definitions')
        d.clear()
        d.update(n)
