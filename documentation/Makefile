
all: help

build:
	sphinx-build -b html -d _build/doctrees   . _build/html
	lyx -batch -E pdf _build/html/getpvs-manual.pdf getpvs-manual.lyx
	touch _build/html/.nojekyll

commit: build
	./commitdir.sh gh-pages $$PWD/_build/html
