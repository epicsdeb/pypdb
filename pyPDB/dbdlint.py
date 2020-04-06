# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

from __future__ import print_function

import logging
_log = logging.getLogger(__name__)
# special logger for lint results
_msg = logging.getLogger("dbdlint")
_msg.propagate = False

import sys, re, itertools

from .dbd.yacc import parse
from .dbd.ast import Code, Comment, Block, Command, DBSyntaxError

_dft_warns = {
    'quoted':"A node argument isn't quoted",
    'varint':"A varaible(varname) node which doesn't specify a type, which defaults to 'int'",
    'spec-comm':"Syntax error in special #: comment line"
}

_all_warns = {
    'ext-link':"A DB/CA link to a PV which is not defined.  Add '#: external(\"pv.FLD\")",
    'bad-field':"Unable to validate record instance field due to a previous error (missing recordtype).",
    'rec-append':"Not using Base >=3.15 style recordtype \"*\" when appending/overwriting record instances",
}
_all_warns.update(_dft_warns)

def getargs(args=None):
    import argparse
    P = argparse.ArgumentParser(description='DB/DBD file validator')
    P.add_argument('input', nargs='+', help='.db or .dbd files')
    P.add_argument('-P','--partial', action='store_false', dest='whole', default=False,
                   help='Database fragment validation')
    P.add_argument('-F','--full', action='store_true', dest='whole',
                   help='Validate as complete database')
    P.add_argument('-l','--log-lvl', type=logging.getLevelName, default='WARN',
                   help='Logging level (default WARN)')
    P.add_argument('-W', '--warn', metavar='TAG', action='append', default=None,
                   help="Use -Wlist to see a list of allowed tags "+\
                       "May be '-Wno-...' to disable a warning"+\
                       ", '-Werror' to treat warnings as errors, "+\
                       "or '-Wnone' to disable all warnings.  "+\
                       "May be given multiple times.")

    P.add_argument('-d','--dbst', action='store_true', default=False,
                   help='Enable dbst compatibility mode')

    P.add_argument('--skip', action='store_true',
                   help='Exit immediately with success.  No checking is done')
    P.add_argument('--hotshot', metavar='FILE',
                   help='Run with Hotshot profiller')

    args = P.parse_args(args=args)

    if args.dbst:
        # dbst compatibility mode is meant to be invoked as:
        #  out.db: in.db
        #     $(DBST) . $< -d > $@
        if len(args.input)!=2 or args.input[0]!='.':
            P.error("dbst mode must be '<exe> . <dbfile> -d'")
        args.input.pop(0)

    args.werror = False
    if args.warn is None:
        args.warn = set(_dft_warns)

    else:
        warn = set(_dft_warns.keys())
        for W in args.warn:
            if W=='list':
                from textwrap import TextWrapper
                F = sys.stderr
                F.write("Warning tags\n  Warn when ...\n")
                fmt = TextWrapper(initial_indent='  ', subsequent_indent='  ',
                                  width=80)
                for tag,desc in _all_warns.items():
                    F.write("\n-W%s\n"%tag)
                    F.write(fmt.fill(desc))
                    F.write('\n')
                P.exit(status=1)
            elif W=='error':
                args.werror = True
            elif W=='all':
                warn = set(_all_warns.keys())
            elif W=='none':
                warn = set()
            elif W.startswith('no-'):
                W = W[3:]
                warn.discard(W)
            else:
                warn.add(W)

        args.warn = warn

    return args

def readall(args):
    F = []
    for I in args.input:
        with open(I, 'r') as F:
            F.append(parse(I, file=I))

    return F

def main(args):
    if args.skip:
        sys.exit(0)
    R = Results(args)
    for I in args.input:
        _log.info('Processing %s', I)
        try:
            with open(I, 'r') as F:
                content = F.read()
            if args.dbst:
                sys.stdout.write(content)
            dbd = parse(content, file=I)
            walk(dbd, dbdtree, R)
        except DBSyntaxError as e:
            R._error = True
            _msg.error(e.args[0], extra={'dbfile':e.fname,
                                         'dbline':e.lineno,
                                         'tag':'syntax'})
        except KeyboardInterrupt:
            R._error = True
            break
        except:
            _log.exception("Error processing %s", I)
            R._error = True

    if len(R.stack)>0:
        _log.error("parent stack not empty at exit: %s", R.stack)
    if R._error:
        sys.exit(2)
    if args.werror and R._warning:
        sys.exit(2)

class Results(object):
    def __init__(self, args):
        self.whole = args.whole
        self._error = False # Set if some syntax/sematic error is encountered
        self._warning = False
        self._wlvl = logging.ERROR if args.werror else logging.WARN
        self._warns = args.warn
        self.node = None
        self.stack = []

        self.rectypes = {} # {'ao':{'OUT':'DBF_OUTLINK', ...}, ...}
        self.recdsets = {} # {'ao':{'Soft Channel':'CONSTANT', ...}, ...}
        self.recinst = {} # {'inst:name':'ao', ...}
        self.extinst = set()

    def err(self, name, msg, *args):
        self._error = True
        _msg.error(msg, extra={'dbfile':self.node.fname,
                               'dbline':self.node.lineno,
                               'tag':name},
                               *args)

    def warn(self, name, msg, *args):
        if name not in self._warns:
            _log.debug("disabled warning %s", name)
            return
        self._warning = True
        _msg.log(self._wlvl, msg, extra={'dbfile':self.node.fname,
                                         'dbline':self.node.lineno,
                                         'tag':name},
                                         *args)

_hwlink_fmts = {
    'INST_IO':'@.*',
    'VME_IO':'#C.+ S.+ @.*',
}

def wholeRectypeField(ent, results, info):
    ft = ent.args[1]
    rt = results.stack[-1].args[0]
    results.rectypes[rt][ent.args[0]] = ft

_lmod = set(['CA','CP','CPP','NMS','MS','MSS','MSI','NPP','PP'])

# Possibilities:
#   recname
#   recname MOD MOD
#   recname.FLD
#   recname.FLD MOD MOD
_fld_pat = re.compile(r'(?:([^. ]+)(?:\.([A-Z][A-Z0-9]+))?(?: ([A-Z ]+))?)?')

def checkRecLink(results, lval):
    '''Validate record (DB or CA) link string

    Call from field() validation
    '''
    try:
        float(lval) # parse as a test for a CONSTANT value
        return
    except ValueError:
        pass
    M = _fld_pat.match(lval)
    if not M:
        results.err('link-format', "Invalid value for Link field '%s'", lval)
        return
    rname, fld, lmod = M.groups()

    lmod = set(lmod.split()) if lmod else set()
    if not fld or fld=='TIME':
        fld = 'VAL'

    if lmod:
        badfld = lmod-_lmod
        if badfld:
            results.err('link-mod', "Invalid link modifier(s) '%s'", ', '.join(badfld))

    try:
        rtype = results.recinst[rname]
    except KeyError:
        extname = '%s.%s'%(rname, fld)
        if extname not in results.extinst:
            results.warn("ext-link", "DB/CA Link to outside PV '%s'", extname)
    else:
        fldinfo = results.rectypes[rtype]
        if fld not in fldinfo:
            results.err('bad-field', "Link to '%s' of type '%s' has no field '%s'",
                        rname, rtype, fld)

def checkRecInstField(ent, results, info):
    if ent.args[0].upper()!=ent.args[0]:
        results.err('field-case', "Field names must be upper case (%s)", ent.args[0])

def wholeRecInstField(ent, results, info):
    recent, fname = results.stack[-1], ent.args[0]
    if not hasattr(recent, '_fieldinfo'):
        results.warn('bad-field', "Unable to validate field '%s'.  Likely due to an earlier error.", fname)
        return
    ftype = recent._fieldinfo.get(fname)
    if not ftype:
        results.err('bad-field', "recordtype '%s' has not field '%s'",
                    recent.args[0], fname)

    elif fname in ['INP', 'OUT']:
        ltype = getattr(recent, '_iolink', 'CONSTANT')
        if ltype=='CONSTANT':
            checkRecLink(results, ent.args[1])
        else:
            try:
                lfmt = _hwlink_fmts[ltype]
                if not re.match(lfmt, ent.args[1]):
                    results.err('hw-link', "Incorrect %s - %s", ltype, ent.args[1])
            except KeyError:
                _log.info("Unsupported link type %s", ltype)

    elif ftype.endswith('LINK'):
        checkRecLink(results, ent.args[1])

    elif fname=='DTYP':
        try:
            recent._iolink = results.recdsets[recent.args[0]][ent.args[1]]
        except KeyError:
            results.err('bad-dtyp', "record type '%s' has no DTYP '%s'",
                        recent.args[0], ent.args[1])

def checkRecType(ent, results, info):
    rtype = ent.args[0]
    results.rectypes[rtype] = {}
    results.recdsets[rtype] = {}

def wholeRecInst(ent, results, info):
    rtype = ent.args[0]
    appending = rtype=='*'
    if rtype=='*' and ent.args[1] in results.recinst:
        rtype = results.recinst[ent.args[1]]

    try:
        ent._fieldinfo = results.rectypes[rtype]
    except KeyError:
        results.err('bad-rtyp', "%s has unknown record type '%s'", ent.args[1], rtype)

    if ent.args[1] in results.recinst:
        otype = results.recinst[ent.args[1]]
        if otype!=rtype:
            results.err('bad-rtyp', "Can't change record '%s' from '%s' to '%s'",
                        ent.args[1], otype, rtype)
        elif not appending:
            results.warn('rec-append', "Append/overwrite with record(\"*\", \"%s\") { ...", ent.args[1])
        else:
            _log.debug("Appending '%s'", ent.args[1])

    else:
        results.recinst[ent.args[1]] = rtype

def checkvar(ent, results, info):
    if len(ent.args)==1:
        results.warn("varint", "No type specified for variable %s, implies 'int'",
                     ent.args[0])

    elif len(ent.args)!=2:
        results.err('bad-args', "variable must have 2 arguments, found %d", len(ent.args))

def wholeDevice(ent, results, info):
    # device(rectype, *_IO, dev*, "DTYP string")
    rtype = ent.args[0]
    if rtype not in results.rectypes:
        results.err('bad-rtyp', "%s has unknown record type %s", ent.args[3], rtype)
    else:
        results.recdsets[rtype][ent.args[3]] = ent.args[1]

def includeFile(ent, results, info):
    results.err('incomplete-dbd', 'This tool must be run on an expanded .dbd.  (eg. softIoc.dbd, not base.dbd)')

# Checks to be applied at specific places in the syntax tree.
dbdtree = {
    Block:{
        'record':{
            'nargs':2,
            'quote':[None, True],
            'wholefn':wholeRecInst,
            'tree':{
                Block:{
                    'field':{
                        'nargs':2,
                        'empty':[False,True],
                        'quote':[None, True],
                        'body':False,
                        'checkfn':checkRecInstField,
                        'wholefn':wholeRecInstField,
                    },
                    'info':{
                        'nargs':2,
                        'quote':[None, True],
                        'body':False,
                    },
                    'alias':{
                        'nargs':1,
                        'quote':[True],
                        'body':False,
                    },
                },
            },
        },
        'recordtype':{
            'nargs':1,
            'wholefn':checkRecType,
            'tree':{
                Block:{
                    'field':{
                        'nargs':2,
                        'quote':[False, False],
                        'wholefn':wholeRectypeField,
                    },
                },
            },
        },
        'alias':{
            'nargs':2,
            'quote':[True,True],
            'body':False,
        },
        'device':{
            'nargs':4,
            'quote':[False,False,False,True],
            'body':False,
            'wholefn':wholeDevice,
        },
        'registrar':{
            'nargs':1,
            'quote':[False],
            'body':False,
        },
        'function':{
            'nargs':1,
            'quote':[False],
            'body':False,
        },
        'variable':{
            'body':False,
            'checkfn':checkvar,
        },
        'menu':{
            'nargs':1,
            'body':True,
        },
        'driver':{
            'nargs':1,
            'body':False,
        },
        'breaktable':{
            'nargs':1,
            'body':True,
        },
        'link':{
            'nargs':2,
            'body':False,
        },
    },
    Command:{
        'include':{
            'quote':True,
            'checkfn':includeFile,
        },
    },
}

def checkEmpty(strs, results, info):
    empty = itertools.chain(info.get('empty',[]), itertools.repeat(False))
    for i,(S,empty) in enumerate(zip(strs, empty)):
        if S is None:
            continue
        if len(S)==0 and empty is False:
            results.err('empty', "Empty string not allowed in position %d (from zero)"%i)

def walk(dbd, basetree, results):
    Q = [('visit',N,basetree) for N in dbd]

    while len(Q):
        ent = Q.pop(0)
        if ent[0]=='push':
            results.stack.append(ent[1])
            continue
        elif ent[0]=='pop':
            parent = results.stack.pop()
            assert ent[1] is parent, (parent, ent)
            continue
        elif ent[0]!='visit':
            raise RuntimeError("Invalid Q command: %s", ent)

        cmd, ent, tree = ent
        results.node = ent
        _log.debug("Visit node %s", ent)

        if isinstance(ent, Comment) and ent.value.startswith(': '):
            _log.debug('Special comment: %s', ent.value)
            try:
                specnodes = parse(ent.value[2:])
                for SN in specnodes:
                    if isinstance(SN, Block) and SN.name=='external':
                        results.extinst.add(SN.args[0])
            except DBSyntaxError as e:
                results.warn('spec-comm', "Failed to parse dbdlint special comment: %s",
                             e.message)
            except:
                _log.exception("Error processing special comment: '#%s'", ent.value)

            continue

        try:
            T = tree[type(ent)]
        except KeyError:
            _log.debug('Ignoring node type %s (%s)', type(ent), ent)
            continue

        I = T.get(ent.name)
        if not I:
            results.err('unknown-node', "Unknown node or out of context: %s", ent)
            continue

        if isinstance(ent, Block):
            havebody = ent.body is not None and len(ent.body)>0
            expectbody = I.get('body')

            if expectbody is not None:
                if expectbody and not havebody:
                    results.err('missing-body', "empty body {} not allowed")
                    continue
                elif not expectbody and havebody:
                    results.err('bad-body', "body {} not allowed")
                    continue

            subtree = I.get('tree')
            if havebody and subtree:
                Q.append(('push',ent))
                Q.extend([('visit',N,subtree) for N in ent.body])
                Q.append(('pop',ent))

            nargs = I.get('nargs')
            if nargs is not None and len(ent.args)!=nargs:
                results.err('bad-args', "Incorrect number of arguments for %s.  %d but expect %d",
                            ent.name, len(ent.args), nargs)
    
            checkEmpty(ent.args, results, I)
            quote = I.get('quote')
            if quote is not None:
                qerr = [E is not None and E!=A for E,A in zip(quote, ent.argsquoted)]
                for i,E in itertools.compress(zip(range(1,1+len(quote)),quote), qerr):
                    if E:
                        results.warn("quoted", "'%s' argument %d not quoted", ent.name, i)
                    else:
                        results.warn("quoted", "'%s' argument %d quoted", ent.name, i)

        elif isinstance(ent, Command):
            checkEmpty([ent.arg], results, I)
            quote = I.get('quote')
            if quote is not None and quote ^ ent.argquoted:
                if quote:
                    results.warn("quoted", "'%s' argument not quoted", ent.name)
                else:
                    results.warn("quoted", "'%s' argument quoted", ent.name)

        fn = I.get('checkfn')
        if fn:
            fn(ent, results, I)
        if results.whole:
            fn = I.get('wholefn')
            if fn:
                fn(ent, results, I)
