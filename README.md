
Utilities for working with EPICS PDB files
==========================================

File validating (linting)
-------------------------

The dbdlint tool performs syntax and other checks of individual .db
files, or entire databases (.dbd and .db files).

Naming convention translation
-----------------------------

This manual describes the usage of the getpvs and applypvs utilities
included in the pyPDB package. These tools provide a way to generate
and apply translations in the GNU Gettext PO format. In this way it is
possible to translate EPICS record names using the tools intended for
natual language translation.

The intent is to simplify the application of site record naming
convention rules to externally produced EPICS support modules.

These tools are best suited to work with databases which have large
numbers of records with similar names, either fully expanded, or with
macros. A database with many records with names like `$(P)<Signal>'
(eg. `$(P)$(N)Status') would be a good candidate. However, a database
where record names are entirely defined by macros (`$(P)$(N)') would
likely not benefit from using these tools.
