# -*- coding: utf-8 -*-

import sys
import warnings

from pyparsing import ParseException

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

def loadEntry(name, entry, path=['.'], skip=[]):
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)

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

    except ParseException,e:
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nOn %d (col %d) of %s\n  %s\n  %s'% \
                            (e, e.lineno, e.col, f, e.line, ('-'*(e.col-1)+'^')))
        raise RecursiveError, next, tb

    skip.pop()
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

def loadDBD(name, path=['.'], skip=[]):
    """Recursively read and parse database
    """
    from os.path import realpath
    f=realpath( findFile(name, path, env='DBDPATH') )
    if f in skip:
        raise RecursiveError('Recursive include of "%s"'%f)
    skip.append(f)

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
                                    path=path, skip=skip)
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
                                    path=path, skip=skip)
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

    except ParseException,e:
        _, _, tb = sys.exc_info()
        next=RecursiveError('%s\nOn %d (col %d) of %s\n  %s\n  %s'% \
                            (e, e.lineno, e.col, f, e.line, ('-'*(e.col-1)+'^')))
        raise RecursiveError, next, tb

    skip.pop()
    return dbd

class DBD(object):
    def __init__(self, dbd=None):
        self.recordtypes={}
        self.menus={}
        self.records={}
        if dbd is not None:
            self.load(dbd)

    def load(self, dbd):
        for ent in dbd:
            if ent.what=='menu':
               if ent.name in self.menus:
                   warnings.warn('Skipping duplicate menu '+ent.name)
                   continue
               self.menus[ent.name]=ent.choices

            elif ent.what=='record' or ent.what=='grecord':
               if ent.name in self.records:
                   warnings.warn('Skipping duplicate record '+ent.name)
                   continue
               self.records[ent.name]=(ent.rec, ent.fields)

            elif ent.what=='recordtype':
               if ent.name in self.recordtypes:
                   warnings.warn('Skipping duplicate recordtype '+ent.name)
                   continue
               self.recordtypes[ent.name]=ent.fields
