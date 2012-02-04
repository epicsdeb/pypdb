#!/usr/bin/env python

import sys
import pyparsing

PPV = tuple(map(int,pyparsing.__version__.split('.')))
if PPV<(1,5,2):
	print "Requires pyparsing >= 1.5.2"
	sys.exit(1)

from distutils.core import setup

setup(name='pyPDB', 
          version='0.1', 
          description="Utilities for working with EPICS PDB files", 
          author='Michael Davidsaver', 
          author_email='mdavidsaver@bnl.gov', 
          packages=['pyPDB',
                    'pyPDB.dbd',
                    'pyPDB.dbd.test',
                    'pyPDB.po',
                   ], 
          scripts=['getpvs', 'applypvs'], 
          requires=
            ['pyparsing (>=1.5.2)'],
      )
