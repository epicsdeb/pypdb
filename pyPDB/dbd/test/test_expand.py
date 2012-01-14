# -*- coding: utf-8 -*-

import unittest
import os.path
from pyPDB.dbd import expand, show

files={
    'dbCom.dbd':"""
# Fields shared by all dbds
        field(NAME,DBF_STRING) {
                prompt("Record Name")
                special(SPC_NOMOD)
                size(61)
        }
        field(DESC,DBF_STRING) {
                prompt("Descriptor")
                promptgroup(GUI_COMMON)
                size(41)
        }
""",
    'fieldCom.dbd':"""
    field(VAL, "0")
    field(INP, "@testing")
    info(autoSave, "VAL INP")
    alias("${P}:other")
""",
    'menuTest.dbd':"""
menu(menuTest) {
        choice(menuTestA,"A")
        choice(menuTestB,"B")
}
""",
    'simpleRecord.dbd':"""
include "menuTest.dbd"
recordtype(simple) {
\tinclude "dbCom.dbd"
\tfield(VAL,DBF_NOACCESS) {
\t\tprompt("Value")
\t\tasl(ASL0)
\t\tspecial(SPC_DBADDR)
\t\tpp(TRUE)
\t\textra("void *           val")
\t}
\tfield(INP,DBF_INLINK) {
\t\tprompt("Input Specification")
\t\tpromptgroup(GUI_COMPRESS)
\t\tinterest(1)
\t}
}
record(simple, "${P}")
{
    include "fieldCom.dbd"
    field(DESC, "Hello world")
}
breaktable(typeJdegC) {
        0.000000 0.000000
        365.023256 67.000000
}
"""
}

# fully expanded version
full="""menu(menuTest) {
    choice(menuTestB,"B")
    choice(menuTestA,"A")
}
recordtype(simple) {
\tfield(NAME,DBF_STRING) {
\t\tprompt("Record Name")
\t\tspecial(SPC_NOMOD)
\t\tsize(61)
\t}
\tfield(DESC,DBF_STRING) {
\t\tpromptgroup(GUI_COMMON)
\t\tprompt("Descriptor")
\t\tsize(41)
\t}
\tfield(VAL,DBF_NOACCESS) {
\t\tpp(TRUE)
\t\textra("void *           val")
\t\tprompt("Value")
\t\tspecial(SPC_DBADDR)
\t\tasl(ASL0)
\t}
\tfield(INP,DBF_INLINK) {
\t\tpromptgroup(GUI_COMPRESS)
\t\tprompt("Input Specification")
\t\tinterest(1)
\t}
}
record(simple,"${P}") {
    field(VAL, "0")
    field(INP, "@testing")
    info(autoSave, "VAL INP")
    alias("${P}:other")
    field(DESC, "Hello world")
}
breaktable(typeJdegC) {
    0.000000 0.000000
    365.023256 67.000000
}
"""

class TestLoad(unittest.TestCase):

    def setUp(self):
        for name,val in files.iteritems():
            f=file(name, 'w')
            f.write(val)
            f.close()

    def test_find(self):
        x=expand.findFile('dbCom.dbd', path=['.'])
        self.assertEqual(x, os.path.join('.','dbCom.dbd'))

        x=expand.findFile('dbCom.dbd', path=[os.getcwd()])
        self.assertEqual(x, os.path.join(os.getcwd(),'dbCom.dbd'))

        x=expand.findFile('dbCom.dbd', path=['wrong','../d%mmy','.'])
        self.assertEqual(x, os.path.join('.','dbCom.dbd'))

        def tst():
            x=expand.findFile('dbCom.dbd', path=['wrong','../d%mmy'])
        self.assertRaises(IOError, tst)

    def test_include(self):

        dbd=expand.loadDBD('simpleRecord.dbd', path=['.'])

        self.assertEqual(dbd[2].name.file, 'simpleRecord.dbd')
        self.assertEqual(dbd[2].name.lineno, 18)
        self.assertEqual(dbd[2].fields[1].value.file, 'fieldCom.dbd')
        self.assertEqual(dbd[2].fields[1].value.lineno, 3)
        self.assertEqual(dbd[2].fields[4].value.file, 'simpleRecord.dbd')
        self.assertEqual(dbd[2].fields[4].value.lineno, 21)

        f=open('expand.dbd', 'w')
        show.showDBD(dbd, f)
        f.close()

        def oops():
            skip=[os.path.realpath(os.path.join('.','simpleRecord.dbd'))]
            dbd=expand.loadDBD('simpleRecord.dbd', path=['.'], skip=skip)

        self.assertRaises(expand.RecursiveError, oops)

        f=open('expand.dbd', 'r')
        check=f.read()
        f.close()

        if check!=full:
            #print '\n',str(check)
            #print '\n',str(full)
            import difflib
            for line in difflib.unified_diff(check.splitlines(),
                                             full.splitlines(),
                                             'actual', 'expected'):
                print line
        self.assertEqual(check, full)
