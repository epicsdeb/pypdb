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

Or to disable warnings entirely give *-Wnone*.

Arguments
---------

.. command-output:: dbdlint -h

Validation Modes
----------------

By default, or when **--partial** is given, only local validation is done.
In the case of *wrong.db* no test is made to see if **xao** is a valid
recordtype.

When **--full** is given, additional validation is done which requires
a complete database (including **recordtype()** definitions).
This allows a number of additional errors and warnings to be emitted.

Error Tags
----------

syntax
~~~~~~

This tag indicates a parsing error, which can occur in many situations.
For example, the line ``field(VAL, " )`` will result in a parsing error since a
quoted string is not closed. ::

    ERROR   badsyntax.db:2 syntax - Missing closing quote on line 2

While a similar line where the closing parenthesis ``)`` is missing
would result a different error since the closing bracket ``}`` is encountered
instead of the parenthesis. ::

    $ echo 'record(ai, "foo") { field(BAR, "oops" }' > badsyntax.db
    $ dbdlint badsyntax.db
    ERROR   badsyntax.db:1 syntax - Syntax error at or before }

If the error is found at the end of the file, the message is again different. ::

    $ echo 'record(ai, "foo") { field(BAR, "oops"' > badsyntax.db
    $ dbdlint badsyntax.db
    ERROR   badsyntax.db:1 syntax - Syntax error near end of input

bad-args
~~~~~~~~

Indicates that the number of arguments of a ``name(args ...)`` block
is incorrect.

link-format
~~~~~~~~~~~

The format of a PV link field is not a number or a PV name (with optional field and modifiers).

link-mod
~~~~~~~~

A PV link contains modifiers not in the set: CA, CP, CPP, MS, MSS, or MSI.

bad-field
~~~~~~~~~

The field referenced is not defined by the associated record type.
This is detected when a field block (``field(NAME, "")``) references a non-existant name,
or when such a link is made to a non-existant name (``field(INP, "foo.INVALID")``).

field-case
~~~~~~~~~~

Field names must be upper case.

hw-link
~~~~~~~

The format of a hardware link value (ie. INST_IO) is not correct.

bad-rtyp
~~~~~~~~

A ``recordtype(name)`` name is mentioned without first being defined.

unknown-node
~~~~~~~~~~~~

A block with an unknown name is encountered (eg. ``feild()``).
Typically a spelling error.

missing-body
~~~~~~~~~~~~

A block is expected to have a body (eg. ``{ <something> }``).

bad-body
~~~~~~~~

A block is **not** expected to have a body, but one was found.

Warning Tags
------------

quoted
~~~~~~

Record instance names (``record(ai, "name")``)
and instance field values (``field(INP, "name")``)
should be quoted.

The IOC's parsing allows unquoted values,
but other parsers (eg. VDCT) treat this as a syntax error.

varint
~~~~~~

A variable block should include a C type as a second argument
(``variable(myInt,int)``).
If omitted, the default is 'int'.

ext-link
~~~~~~~~

A PV link which does not target a defined record, and now external definition
is provided.
An external definition can be added if the PV name with: ::

    #: external("rec:name.FLD")

This warning is not enabled by default.
Either *-Wext-link* or *-Wall* must be given.

spec-comm
~~~~~~~~~

Syntax error in special dbdlint control comment.
This is considered a warning on the chance that some other program
also uses the sequence ``#: ...``.
