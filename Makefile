#!/bin/make


# AUTHOR:  Chris Reid <spikeysnack@gmail.com> #
# LICENSE: Free for all purposes              #
# COPYRIGHT: 2020 - Chris Reid                #

# modification allowed 
# but original attribution stays, add your name to any mods 
# no guarantees implied or inferred
# standard python 
# to install: "just type make"


SHELL = /bin/sh
PY=$(shell which python3)
prefix= $(HOME)
#prefix = /usr/local
bindir = $(prefix)/bin
mandir = $(prefix)/share/man
manext = 7
docdir = $(prefix)/share/doc/playlist
INSTALL = $(shell which install)
INSTALL_PROGRAM = $(INSTALL)
DESTNAME= "playlist"

#.PHONY: install install-bin uninstall


.DEFAULT: help

help:
	@echo "make all"
	@echo "       install bin, man, docs"
	@echo
	@echo "make install-bin"
	@echo "       install binto user bin directory"
	@echo
	@echo "make install-man"
	@echo "       install manpage to user man directory"
	@echo
	@echo "make install-doc"
	@echo "       install docs to user doc directory"
	@echo
	@echo "make uninstall"
	@echo "       remove bin,man,doc"
	@echo
	@echo "make update"
	@echo "       get latest from github"
	@echo
	@echo "make readme"
	@echo "       read README file"


all:	playlist.py install

install:	playlist.py install-bin install-man install-doc
	@echo "$(DESTNAME) installed to $(bindir)"
	@echo "manpage installed to $(mandir)"
	@echo "docs installed to $(docdir)"

install-bin:	playlist.py
	$(INSTALL_PROGRAM) -p  --mode=0755  playlist.py $(bindir)/
	ln -sf $(bindir)/playlist.py $(bindir)/playlist

install-man:	playlist.py doc/playlist.7
	mkdir -p $(mandir)
	$(INSTALL_PROGRAM) -d -g users --mode=0755 $(mandir)/man$(manext)
	$(INSTALL_PROGRAM) --mode=0644 doc/playlist.7 $(mandir)/man$(manext)/

install-doc:	playlist.py
	mkdir -p $(docdir)
	$(INSTALL_PROGRAM) -d -g users --mode=0755 $(docdir)
	cp -a doc/* $(docdir)

uninstall:
	rm  -f $(bindir)/playlist.py
	@echo "$(DESTNAME) removed from $(bindir)"
	rm  -f $(mandir)/playlist.7 
	@echo "manpage removed from $(mandir)"
	rm  -rf $(docdir) 
	@echo "docs removed from $(docdir)"

update:
	@{ GF=$(shell git fetch origin 2>&1); \
	   if [[ "$${GF}" ]]  ; then git merge origin ; \
	   else     echo "playlist is already up to date." ; fi }

readme:	README.md
	@less README.md

clean:
	@rm -f *~ 





