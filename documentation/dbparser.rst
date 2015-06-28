DB/DBD Grammar
==============

The DB/DBD file grammer as understood by pyPDB begins with :token:`nodelist`.

.. productionlist::
    nodelist : `node` `nodelist`
             : `node`
             : `empty`
    node     : `block`
             : `command`
             : `CODE`
             : `COMMENT`
    block : `BARE` '(' `arglist` ')' '{' `nodelist` '}'
          : `BARE` '(' `arglist` ')'
    command : `BARE` `BARE`
            : `BARE` `QUOTED`
    arglist : `value` ',' `arglist`
            : `value`
            : `empty`
    value : `QUOTED`
          : `bval`
    bval : `BARE` `bval`
         : `MACRO` `bval`
         : `BARE`
         : `MACRO`
    empty :
    BARE : [a-zA-Z0-9_+:.\[\]<>;-]+
    QUOTED : "(?:\\.|[^"\n])*"
    MACRO : '$'[({] ... [)}] # tokenizing is stateful, see lex.py
    CODE : '%' [^\n]* '\n'
    COMMENT : '#' [^\n]* '\n'

Limitations
-----------

The DB/DBD parser of pyPDB has some limitations when compared with the
IOC parser.

The IOC parser (dbStatic) is effectively two pass parsing in that
macros (eg. ``$(NAME)``) are expanded line-by-line before
lexing.
It is possible for macros to modify syntax.
For example: ::

    record($(MAC)) {}

could be a valid as an expansion of *$(MAC)* could include a comma
 (``MAC=ai\,"bar"``).  The following loads an *ai* record named *rec:name*.  ::

.. code-block:: sh

    $ echo 'record($(MAC)) {}' > wierd.db
    $ softIoc -m 'MAC=ai\,"rec:name"' -d wierd.db

The pyPDB parser **does not perform macro expansion**.
Instead it treats macros as tokens.
It will fail to parse, or emit errors, when macros appear
which would cross token boundaries.

Macros may appear within a quoted string. ::

    field(NELM, "$(NELM=100)")

Unquoted macros may appear within, or in place of, Block arguments. ::

    field(NELM, $(NELM=100))
    field($(NAME), $(VALUE))

Macros may **not** appear in place of keywords, nor in place of literals. ::

    $(TAG)(A, "B")          # Fails
    field $(LPAREN) A, "B") # Fails
