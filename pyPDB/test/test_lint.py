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
        F = logging.Formatter('%(levelname)s|%(dbfile)s:%(dbline)s|%(tag)s|%(message)s')
        self.setFormatter(F)
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
            self.msg[rec.levelno].append(self.format(rec))
        except KeyError:
            pass

class _TestLint(unittest.TestCase):
    def _matchmsg(self, file, type, Lactual, Lexpect):
        Lexpect = Lexpect or []
        for expect, actual in zip(Lexpect, Lactual):
            M = re.match(expect, actual)
            if M is None:
                raise self.failureException("%s '%s' not mached by '%s'"%(type, actual, expect))
        if len(Lexpect)!=len(Lactual):
            self.assertListEqual(Lexpect, Lactual)

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

        if errors or (args.werror and warnings):
            expectcode = 2
        else:
            expectcode = 0

        if expectcode!=code:
            raise self.failureException("expected exit code %d, actual %d"%(expectcode,code))

class TestLint(_TestLint):
    def test_good(self):
        self.assertLint("good.db", args=['-Wall', '-F'],
                        warnings=[
            r'.*/good.db:12|rec-append|Append/overwrite.*',
        ])

    def test_badsyntax(self):
        self.assertLint("badsyntax.db", errors=['.*Syntax error at or before }'])

    def test_argno(self):
        self.assertLint("argno.db", errors=[
            '.*/argno.db:1|bad-args|.*record.* 1 but expect 2',
            '.*/argno.db:2|bad-args|.*field.* 3 but expect 2',
        ])

    def test_fieldname(self):
        self.assertLint("fieldname.db", errors=[
            r'.*/fieldname.db:2|field-case|.*dTYP.*',
        ])

    def test_quote(self):
        self.assertLint("quote.db", warnings=[
            r".*/quote.db:1|quoted|.*record.* 2 not quoted",
            r".*/quote.db:5|varint|.*foo.*",
            r".*/quote.db:2|quoted|.*field.* 2 not quoted",
        ])

        # treat warnings as errors
        self.assertLint("quote.db", errors=[
            r".*/quote.db:1|quoted|.*record.* 2 not quoted",
            r".*/quote.db:5|varint|.*foo.*",
            r".*/quote.db:2|quoted|.*field.* 2 not quoted",
        ], args=['-Werror'])

        # disable warning
        self.assertLint("quote.db", args=['-Wnone'])

        # enable only this warning
        self.assertLint("quote.db", warnings=[
            r".*/quote.db:1|quoted|.*record.* 2 not quoted",
            r".*/quote.db:2|quoted|.*field.* 2 not quoted",
        ], args=['-Wnone', '-Wquoted'])

    def test_fieldlinks(self):
        self.assertLint("fields.db", warnings=[
            r'.*/fields.db:6|bad-field|Unable to validate field \'VAL\'',
            r'.*/fields.db:31|ext-link|.*missing.RVAL',
        ], errors=[
            r'.*/fields.db:2|bad-rtyp|.*Soft Channel .* aaa',
            r'.*/fields.db:5|bad-rtyp|.*unknown record type aaa',
            r'.*/fields.db:15|bad-rtyp|.*abc',
            r'.*/fields.db:19|hw-link|.*VME_IO.*',
        ], args=['-Wall', '--full'])

    def test_switchrtyp(self):
        self.assertLint("switchrtyp.db", args=['-F'], errors=[
            r".*/switchrtyp.db:19|bad-rtyp|.*change record 'blah' from 'xyz' to 'other'",
        ])
