#!/usr/bin/env python

from distutils.core import setup, Command, Distribution
from distutils.command import build, build_py

import sys, os
try:
    from importlib import import_module
except ImportError:
    def import_module(name): # stripped down version
        __import__(name)
        return sys.modules[name]


class GenPLY(Command):
    """Generate lextab.py and parsetab.py
    """
    user_options = [
        ('build-lib=', 'd', "directory to \"build\" (copy) to"),
        ('inplace', 'i',
        "ignore build-lib and put compiled extensions into the source " +
        "directory alongside your pure Python modules"),
    ]
    def initialize_options(self):
        self.build_lib = None
        self.inplace = 0

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))
        self.set_undefined_options('build_ext',
                                   ('inplace','inplace'))
        self.ply = self.distribution.x_ply
        print 'build_lib',self.build_lib

    def run(self):
        from ply import lex, yacc
        orig = os.getcwd()
        if self.inplace:
            base = orig
        else:
            base = os.path.join(orig, self.build_lib)
        print 'base', base
        try:
            for L, Y in self.ply:
                M = import_module(L)
                D = os.path.join(base, os.path.relpath(os.path.dirname(M.__file__), orig))

                print "Generating Lex table from %s in %s"%(L,D)
                if not self.dry_run:
                    self.mkpath(D)
                    os.chdir(D) # Needed for PLY <3.6
                    lex.lex(module=M, optimize=1, lextab='lextab')

                M = import_module(Y)
                D = os.path.join(base, os.path.relpath(os.path.dirname(M.__file__), orig))

                print "Generating Yacc table from %s in %s"%(L,D)
                if not self.dry_run:
                    self.mkpath(D)
                    os.chdir(D) # Needed for PLY <3.6
                    yacc.yacc(module=M, optimize=1, tabmodule='parsetab')
        finally:
            os.chdir(orig)

Distribution.x_ply = None

print 'build commends',build.build.sub_commands
# after build_py
build.build.sub_commands.append(('build_ply', lambda cmd:True))

setup(name='pyPDB', 
          version='0.1', 
          description="Utilities for working with EPICS PDB files", 
          author='Michael Davidsaver', 
          author_email='mdavidsaver@bnl.gov', 
          packages=['pyPDB',
                    'pyPDB.dbd',
                    'pyPDB.po',
                   ], 
          scripts=['getpvs', 'applypvs'], 
          requires=
            ['ply (>=3.4)'],

          cmdclass={
              'build_ply':GenPLY,
          },
          x_ply = [('pyPDB.dbd.lex','pyPDB.dbd.yacc')],
      )
