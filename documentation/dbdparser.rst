DB/DBD File Parser API
======================

:mod:`pyPDB.dbd` Module
-----------------------

.. module:: pyPDB.dbd
   :synopsis: DB/DBD File Parser

.. autofunction:: parse

.. autoclass:: Block

.. autoclass:: Command

.. autoclass:: Comment

.. autoclass:: Code

.. autoclass:: DBSyntaxError

   A sub-class of :class:`RuntimeError` thrown by :func:`parse`.

   .. attribute:: fname

      The file name where the error occured.

   .. attribute:: lineno

      The line number where the error occured.

.. autofunction:: quote
