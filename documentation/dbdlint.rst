DB/DBD File Validator (dbdlint)
===============================

.. highlight:: sh

The **dbdlint** program validates the contents of one or more .db or .dbd files.
It applies a number of checks beyond simple syntax tests.

It can simply be used to check a single file like: ::

    $ echo "record(xao, some:name) {}" > wrong.db
    $ dbdlint wrong.db
    WARNING wrong.db:1 - 'record' argument 2 not quoted
    $ echo $?
    0

Which shows a warning because *some:name* isn't quoted.
To make the warning an error: ::

    $ dbdlint -Werror wrong.db
    ERROR wrong.db:1 - 'record' argument 2 not quoted
    $ echo $?
    2

Validation Modes
----------------

By default, or when *--partial* is given, only local validation is done.
In the case of *wrong.db* no test is made to see if **xao** is a valid
recordtype.
