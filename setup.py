#!/usr/bin/env python

import sys


from setuptools import setup

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
          install_requires=
            ['ply (>=3.4)'],
      )
