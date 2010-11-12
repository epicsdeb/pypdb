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
        include "dbCom.dbd"
        field(VAL,DBF_NOACCESS) {
                prompt("Value")
                asl(ASL0)
                special(SPC_DBADDR)
                pp(TRUE)
                extra("void *           val")
        }
        field(INP,DBF_INLINK) {
                prompt("Input Specification")
                promptgroup(GUI_COMPRESS)
                interest(1)
        }
}
record(simple, "${P}")
{
    include "fieldCom.dbd"
    field(DESC, "Hello world")
}
"""
}

# fully expanded version
full="""menu(menuTest) {
    choice(menuTestB,"B")
    choice(menuTestA,"A")
}
recordtype(simple) {
    field(NAME,DBF_STRING) {
        prompt("Record Name")
        special(SPC_NOMOD)
        size(61)
    }
    field(DESC,DBF_STRING) {
        promptgroup(GUI_COMMON)
        prompt("Descriptor")
        size(41)
    }
    field(VAL,DBF_NOACCESS) {
        pp(TRUE)
        extra("void *           val")
        prompt("Value")
        special(SPC_DBADDR)
        asl(ASL0)
    }
    field(INP,DBF_INLINK) {
        promptgroup(GUI_COMPRESS)
        prompt("Input Specification")
        interest(1)
    }
}
record(simple,"${P}") {
    field(VAL, "0")
    field(INP, "@testing")
    info(autoSave, "VAL INP")
    alias("${P}:other")
    field(DESC, "Hello world")
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
