# -*- coding: utf-8 -*-
"""
Copyright (c) 2012 Brookhaven Science Associates, as Operator of
    Brookhaven National Laboratory.
pyPDB is distributed subject to a Software License Agreement found
in file LICENSE that is included with this distribution.
"""

import unittest
import pyPDB.dbd.grammer as dbd
from pyPDB.dbd.show import showDBD

class TestDbd(unittest.TestCase):
    
    def test_double(self):
        vals=[('4', 4.0), 
                  ('4.1',  4.1),
                  ('+4.1',  4.1),
                  ('.4',  0.4),
                  ('-.4',  -0.4),
                  ('-00.004',  -0.004),
                  ('0e0',  0.0),
                  ('-1e-5',  -1e-5),
                  ('-1e5',  -1e5),
                  ('1e-5',  1e-5),
                  ('1e-5',  1e-5),
                ]
        for s, f in vals:
            x=dbd.Double.parseString(s)
            self.assertEqual(x[0], f)
    
    def test_menu(self):
        x=dbd.MenuHead.parseString("menu(XXX)", parseAll=True)
        self.assertEqual(x.asList(), ['menu','XXX'])
        self.assertEqual(x.what, 'menu')
        self.assertEqual(x.name, 'XXX')

        x=dbd.MenuEntry.parseString('choice(menu_x,"4 second")', parseAll=True)
        self.assertEqual(x.asList(), [['menu_x', '4 second']])

        mscan="""
menu(menuScan) {
        choice(menuScanPassive,"Passive")
        choice(menuScanEvent,"Event")
        choice(menuScanI_O_Intr,"I/O Intr")
        choice(menuScan10_second,"10 second")
        choice(menuScan5_second,"5 second")
        choice(menuScan2_second,"2 second")
        choice(menuScan1_second,"1 second")
        choice(menuScan_5_second,".5 second")
        choice(menuScan_2_second,".2 second")
        choice(menuScan_1_second,".1 second")
}
"""
        choices={"menuScanPassive":"Passive",
                "menuScanEvent":"Event",
                "menuScanI_O_Intr":"I/O Intr",
                "menuScan10_second":"10 second",
                "menuScan5_second":"5 second",
                "menuScan2_second":"2 second",
                "menuScan1_second":"1 second",
                "menuScan_5_second":".5 second",
                "menuScan_2_second":".2 second",
                "menuScan_1_second":".1 second",
                }

        x=dbd.Menu.parseString(mscan, parseAll=True)
        self.assertEqual(x.asList(), ['menu',"menuScan", choices])
        self.assertEqual(x.what, 'menu')
        self.assertEqual(x.name, "menuScan")
        self.assertEqual(x.choices, choices)

    def test_ccode(self):
        x=dbd.CCode.parseString(' %struct aSubRecord;', parseAll=True)
        self.assertEqual(x.asList(), ['CCode','struct aSubRecord;'])
        self.assertEqual(x.what, 'CCode')
        self.assertEqual(x.code, 'struct aSubRecord;')

    def test_value(self):
        for inp,exp in [('  " test value "  ', [' test value ']),
                        ('test value', ['test value']),
                        ('  test value ', ['test value']),
                        ('  $(P) ', ['$(P)']),
                        ('  test$(P)ing ', ['test$(P)ing']),
                        ('  test $(P)ing ', ['test $(P)ing']),
                       ]:

            x=dbd.DBValue.parseString(inp, parseAll=True)
            self.assertEqual(x.asList(), exp)

    def test_field(self):
        x=dbd.RecordFieldHead.parseString("field(INP,DBF_INLINK)", parseAll=True)
        self.assertEqual(x.asList(), ['field','INP','DBF_INLINK'])

        for I,O in [('prompt("Value")', ['prompt', 'Value']),
                    ('initial("this is a test")', ['initial', 'this is a test']),
                    ('asl(ASL1)', ['asl', 'ASL1']),
                    ('interest(1)', ['interest', '1']),
                   ]:
            x=dbd.RecordFieldAttr.parseString(I, parseAll=True)
            self.assertEqual(x.asList(), O)

        fld="""
        field(ALG,DBF_MENU) {
                prompt("Compression Algorithm")
                promptgroup(GUI_ALARMS)
                special(SPC_RESET)
                interest(1)
                menu(compressALG)
        }
        """
        fattrs={'promptgroup': 'GUI_ALARMS',
                'menu': 'compressALG',
                'prompt': 'Compression Algorithm',
                'interest': '1',
                'special': 'SPC_RESET'}

        x=dbd.RecordField.parseString(fld, parseAll=True)
        self.assertEqual(x.what, 'field')
        self.assertEqual(x.name, "ALG")
        self.assertEqual(x.dbf, "DBF_MENU")
        self.assertEqual(x.attrs, fattrs)

    def test_record(self):
        x=dbd.RecordHead.parseString("recordtype(compress)", parseAll=True)
        self.assertEqual(x.asList(), ['recordtype','compress'])

        rec="""
recordtype(compress) {
        include "dbCommon.dbd"
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
        field(RES,DBF_SHORT) {
                prompt("Reset")
                asl(ASL0)
                special(SPC_RESET)
                interest(3)
        }
}
"""

        x=dbd.Record.parseString(rec, parseAll=True)
        self.assertEqual(x.what, 'recordtype')
        self.assertEqual(x.name, "compress")
        self.assertEqual(x.fields.asList(), [
                    ['include', 'dbCommon.dbd'],
                    ['field', 'VAL', 'DBF_NOACCESS',
                        {'pp': 'TRUE',
                         'extra': 'void *           val',
                         'prompt': 'Value',
                         'special': 'SPC_DBADDR',
                         'asl': 'ASL0'}],
                    ['field', 'INP', 'DBF_INLINK',
                        {'promptgroup': 'GUI_COMPRESS',
                         'prompt': 'Input Specification',
                         'interest': '1'}],
                    ['field', 'RES', 'DBF_SHORT',
                        {'prompt': 'Reset',
                         'interest': '3',
                         'special': 'SPC_RESET',
                         'asl': 'ASL0'}],
                   ])

    def test_inst(self):
        """Record Instance
        """
        inp="""
record (ai, "$(P)") {
    include "favFields.db"
    field(TST,  "testing" )
    field(VAL, test value )
    field(XYZ, $(P))
    info(hELlo, "world")
    alias("$(P):other")
}
        """
        x=dbd.Inst.parseString(inp, parseAll=True)
        self.assertEqual(x.what, "record")
        self.assertEqual(x.rec, "ai")
        self.assertEqual(x.name, "$(P)")
        self.assertEqual(x.name.lineno, 2)
        self.assertEqual(x.fields[1].value.lineno, 4)
        self.assertEqual(x.fields.asList(),
                [['include', 'favFields.db'],
                 ['field', 'TST', 'testing'],
                 ['field', 'VAL', 'test value'],
                 ['field', 'XYZ', '$(P)'],
                 ['info', 'hELlo', 'world'],
                 ['alias', '$(P):other']
                ])

        inp="""
grecord (ai, "yy$(P)xx") {
    include "favFields.db"
    field(FFF, test)
}
"""
        x=dbd.Inst.parseString(inp, parseAll=True)
        self.assertEqual(x.what, "grecord")
        self.assertEqual(x.rec, "ai")
        self.assertEqual(x.name, "yy$(P)xx")
        self.assertEqual(x.name.lineno, 2)
        self.assertEqual(x.fields[1].value.lineno, 4)
        self.assertEqual(x.fields.asList(),
                [['include', 'favFields.db'],
                 ['field', 'FFF', 'test'],
                ])

    def test_dbd(self):
        inp="""
# testing
menu(menuScan) {
        choice(menuScanPassive,"Passive")
        choice(menuScanI_O_Intr,"I/O Intr")
        # hello
        choice(menuScan_1_second,".1 second")
}
# one two

recordtype(Compress) {
        # world
        include "dbCommon.dbd"
        field(VAL,DBF_NOACCESS) {
                prompt("Value")
                asl(ASL0) # this is a comment
                special(SPC_DBADDR)
                pp(TRUE)
                extra("void *           val")
        }
        field(INP,DBF_INLINK) { # oops
                prompt("Input Specification")
                promptgroup(GUI_COMPRESS)
                interest(1)
        } # hi
}
"""

        x=dbd.DBD.parseString(inp, parseAll=True)
        self.assertEqual(len(x),2)
        self.assertEqual(x[0].asList(), ['menu', 'menuScan',
            {'menuScan_1_second': '.1 second',
             'menuScanPassive': 'Passive',
             'menuScanI_O_Intr': 'I/O Intr'
            }])
        self.assertEqual(x[1].asList(), ['recordtype', 'Compress',
            [['include', 'dbCommon.dbd'],
             ['field', 'VAL', 'DBF_NOACCESS',
                {'pp': 'TRUE',
                 'extra': 'void *           val',
                 'prompt': 'Value',
                 'special': 'SPC_DBADDR',
                 'asl': 'ASL0'}],
             ['field', 'INP', 'DBF_INLINK',
                {'promptgroup': 'GUI_COMPRESS',
                 'prompt': 'Input Specification',
                 'interest': '1'}]
             ]
           ])
    
    def test_bpt(self):
        x=dbd.BPTHead.parseString("breaktable(bptXj4sd)", parseAll=True)
        self.assertEqual(x.asList(), ['breaktable','bptXj4sd'])
        self.assertEqual(x.what, 'breaktable')
        self.assertEqual(x.name, 'bptXj4sd')
        
        x=dbd.BPTLine.parseString('365.023256 67.000000', parseAll=True)
        self.assertEqual(x.asList(), [365.023256,  67.0])
        
        T="""
  breaktable(typeJdegC) {
        0.000000 0.000000
        365.023256 67.000000
        1000.046512 178.000000
        3007.255814 524.000000
        3543.383721 613.000000
        4042.988372 692.000000
        4101.488372 701.000000
}"""
        F=[[0.0, 0.0],
             [365.023256, 67.0],
             [1000.046512, 178.0],
             [3007.2558140000001, 524.0],
             [3543.3837210000002, 613.0],
             [4042.9883719999998, 692.0],
             [4101.4883719999998, 701.0], 
            ]

        x=dbd.BPT.parseString(T,  parseAll=True)
        self.assertEqual(x.what, 'breaktable')
        self.assertEqual(x.name, 'typeJdegC')
        self.assertEqual(len(x.table), len(F))
        for A,E in zip(x.table,  F):
            self.assertEqual(A.asList(),  E)
