# -*- coding: utf-8 -*-
"""
Copyright (c) 2015 Michael Davidsaver
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import os, re, logging
import unittest

from .. import dbdlint

_testdata = os.path.dirname(__file__)

class CaptureMsg(logging.Handler):
    def __init__(self, lvl=logging.WARN):
        self._lvl = lvl
        logging.Handler.__init__(self)
        self._fmt = logging.Formatter('%(levelname)s %(message)s')
        self.reset()
    def __enter__(self):
        L = self._log = logging.getLogger("dbdlint")
        L.addHandler(self)
        L.setLevel(self._lvl)
        L.propagate = False
    def __exit__(self, A, B, C):
        self._log.removeHandler(self)
    def reset(self):
        self.msg = {logging.WARN:[], logging.ERROR:[]}
    def emit(self, rec):
        try:
            self.msg[rec.levelno].append(rec)
        except KeyError:
            pass

class _TestLint(unittest.TestCase):
    def _matchmsg(self, file, type, Lactual, Lexpect):
        missing = []
        for expect in Lexpect or []:
            found = False
            for actual in Lactual:
                msg = actual.getMessage()
                M = re.match(expect, msg)
                if M is not None:
                    found = True
                    Lactual.remove(actual)
                    break
            if not found:
                missing.append(expect)

        for actual in Lactual:
            raise self.failureException("Un-expected %s: '%s'"%(type, actual.getMessage()))

        for expect in missing:
            raise self.failureException("%s did not raise %s '%s'"%(file, type, expect))

    def assertLint(self, file, errors=None, warnings=None, args=None):
        args = args or []
        args.append(os.path.join(_testdata, file))
        args = dbdlint.getargs(args)
        C = CaptureMsg()
        with C:
            code = 0
            try:
                dbdlint.main(args)
            except SystemExit as e:
                code = e.code

        self._matchmsg(file, "warning", C.msg[logging.WARN], warnings)
        self._matchmsg(file, "error", C.msg[logging.ERROR], errors)

        if errors or args.werror:
            expectcode = 2
        else:
            expectcode = 0

        if expectcode!=code:
            raise self.failureException("expected exit code %d, actual %d"%(expectcode,code))

class TestLint(_TestLint):
    def test_badsyntax(self):
        self.assertLint("badsyntax.db", errors=['.*Syntax error at or before }'])

    def test_argno(self):
        self.assertLint("argno.db", errors=[
            '.*/argno.db:1.*Incorrect number of arguments for record.  1 but expect 2',
            '.*/argno.db:2.*Incorrect number of arguments for field.  3 but expect 2',
        ])

    def test_fieldname(self):
        self.assertLint("fieldname.db", errors=[
            r'.*/fieldname.db:2.*Field names must be upper case \(dTYP\)',
        ])

    def test_quote(self):
        self.assertLint("quote.db", warnings=[
            r".*/quote.db:1.*'record' argument 2 not quoted",
            r".*/quote.db:3.*'field' argument 2 not quoted",
            r".*/quote.db:5.*No type specified for variable foo.*",
        ])

        # treat warnings as errors
        self.assertLint("quote.db", errors=[
            r".*/quote.db:1.*'record' argument 2 not quoted",
            r".*/quote.db:3.*'field' argument 2 not quoted",
            r".*/quote.db:5.*No type specified for variable foo.*",
        ], args=['-Werror'])

        # disable warning
        self.assertLint("quote.db", args=['-Wnone'])

        # enable only this warning
        self.assertLint("quote.db", warnings=[
            r".*/quote.db:1.*'record' argument 2 not quoted",
            r".*/quote.db:3.*'field' argument 2 not quoted",
        ], args=['-Wnone', '-Wquoted'])
