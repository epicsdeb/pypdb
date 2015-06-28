Naming Convention Translation
=============================

The **getpvs** and **applypvs** CLI utilities allow the GNU gettext
process for natural languange translation to be applied to
naming convention translation of .db files.
The `manual`_ describes this process in detail.

.. _manual: getpvs-manual.pdf

Template Creation (getpvs)
--------------------------

Parses a file (.db, .edl, or .opi) and generates a PO template file
as a starting point for translation.

.. code-block:: sh

    $ getpvs -o as-4.6.pot -m db -I /usr/lib/epics/dbd -I . base.dbd save_restoreStatus.db
    # or
    $ getpvs -o as-4.6.pot -m edl save_restoreStatus.edl

This template will contain contextual information, including
a list of lines where the record is referenced. ::

    #. recordtype: stringout
    #: save_restoreStatus.db:75
    msgid "$(P)SR_0_Name"
    msgstr ""

The *msgstr* lines should then be filled out with the translated name.
This can be done with any text editor, however specialized PO file
editors like `poedit`_ and `Qt Linguist`_ exist to simplify this process. ::

    #. recordtype: stringout
    #: save_restoreStatus.db:75
    msgid "$(P)SR_0_Name"
    msgstr "$(P)-SR}Name:0-I"

Once translated, this file is typically renamed with the extension *.po*.

.. _poedit: http://www.poedit.net/

.. _Qt Linguist: http://doc.qt.io/qt-5/qtlinguist-index.html

Usage
~~~~~

.. command-output:: getpvs -h

Template Application (applypvs)
-------------------------------

*applypvs* is a specialized (somewhat) context aware bulk search/replace
tool.
It uses a POT file to build a mapping (use *-R* to reverse)
which is then applied to a number of inputs files.

.. code-block:: sh

    $ applypvs -i as-4.6.po -o outdir -m edl some.edl another.edl

Usage
~~~~~

.. command-output:: applypvs -h
