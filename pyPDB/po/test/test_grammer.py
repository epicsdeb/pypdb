# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import unittest
from pyPDB.po.grammer import PO

class TestPO(unittest.TestCase):

    def test_po(self):
        x=PO.parseString('', parseAll=True)
        self.assertEqual(x.asList(), [])

        inp="""msgid ""
msgstr ""
"Project-Id-Version: \\n"
"POT-Creation-Date: \\n"
"PO-Revision-Date: \\n"
"Last-Translator: Michael Davidsaver <mdavidsaver@bnl.gov>\\n"
"Language-Team: \\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=iso-8859-1\\n"
"Content-Transfer-Encoding: 8bit\\n"

#: defined $(P)link:sts.FLNK
msgid "$(P)link:sts:init"
msgstr "$(P)Link:Sts-Init"

#: defined $(P)ts:init.LNK1
msgid "$(P)ts:clock:set"
msgstr ""

#: defined
msgid "$(P)$(CML)pat:dly"
msgstr ""

#: defined $(P)ts:source.OUT
#: $(P)ts:source.FLNK
msgid "$(P)ts:source:raw"
msgstr ""
"""
        expect=[['', ''],
                ['$(P)link:sts:init', '$(P)Link:Sts-Init'],
                ['$(P)ts:clock:set', ''],
                ['$(P)$(CML)pat:dly', ''],
                ['$(P)ts:source:raw', '']
               ]

        x=PO.parseString(inp, parseAll=True)
        self.assertEqual(x.asList(), expect)
