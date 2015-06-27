#!/usr/bin/env python

import sys


from distutils.core import setup

setup(name='pyPDB',
          version='0.1',
          description="Utilities for working with EPICS PDB files",
          author='Michael Davidsaver',
          author_email='mdavidsaver@gmail.com',
          packages=['pyPDB',
                    'pyPDB.dbd',
                    'pyPDB.po',
                   ],
          scripts=['getpvs', 'applypvs', 'dbdlint'],
          requires=
            ['ply (>=3.4)'],
      )
