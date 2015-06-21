# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import sys
import warnings
from copy import copy

from collections import defaultdict
from StringIO import StringIO

from .yacc import parse
from .ast import Command, Block, Comment, Code

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

def loadEntry(name, path=['.'], skip=[], cache=None):
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)

    try:
        return cache[f]
    except KeyError:
        pass

    try:
        with open(f,'r') as F:
            dbd = parse(F.read(), file=name)

        out=[]
        for ent in dbd:
            if isinstance(ent, Command) and ent.name=='include':
                R=loadEntry(ent.arg, path=path, skip=skip)
                out+=R

            elif isinstance(ent, int):
                raise RuntimeError('foo: '+name)
            else:
                out.append(ent)

        dbd=out
    except RecursiveError,e:
        # Append message while preserving stack trace
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nFrom %s'%(e,f))
        raise RecursiveError, next, tb


    skip.pop()
    cache[f]=dbd
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

def loadDBD(name, path=['.'], skip=[], cache=None):
    """Recursively read and parse database
    """
    if cache is None:
        cache = {}
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)
    
    try:
        return cache[f]
    except KeyError:
        pass

    try:
        with open(f,'r') as F:
            dbd = parse(F.read(), file=name)

        out=[]
        for ent in dbd:

            if isinstance(ent, Command) and ent.name=='include':
                R=loadDBD(ent.arg, path=path, skip=skip)
                out+=R

            elif isinstance(ent, Block) and ent.body is not None:
                nf=[]
                for fld in ent.body:
                    if isinstance(fld, Command) and fld.name=='include':
                        R=loadEntry(fld.arg,
                                    path=path, skip=skip, cache=cache)
                        nf+=R

                    else:
                        nf.append(fld)

                ent.body = nf

                out.append(ent)

            else:
                out.append(ent)

        dbd=out
    except RecursiveError,e:
        # Append message while preserving stack trace
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nFrom %s'%(e,f))
        raise RecursiveError, next, tb


    skip.pop()
    cache[f]=dbd
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
            print 'Load',len(dbd)
            self.load(dbd)

    def load(self, dbd):
        # group by type
        for ent in dbd:
            if not isinstance(ent, Block):
                continue
            d=self._dispatch.get(ent.name, None)
            if d is None:
                if ent.name not in ['variable','device','registrar']:
                    warnings.warn("Ignoring %s"%ent)
                continue
            d[ent.args[-1]].append(ent)

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
                    print >>R,'  %s:%d'%(inst.fname, inst.lineno)
            n[name]=ent[0]
        R.seek(0)
        R=R.read()
        if len(R)>0:
            print R
            raise KeyError('duplicate definitions')
        d.clear()
        d.update(n)
