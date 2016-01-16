mcell_main: mcell_main.c libMCell.c libMCell.h libMCell.i makefile
	gcc -c mcell_main.c libMCell.c
	gcc -o mcell_main mcell_main.o libMCell.o
	swig -python libMCell.i
	gcc -c libMCell.c libMCell_wrap.c -fPIC -I/usr/include/python3.4m
	ld -shared libMCell.o libMCell_wrap.o -o _libMCell.so


.PHONY: clean
clean:
	rm -f libMCell.o
	rm -f libMCell.py
	rm -f libMCell_wrap.c
	rm -f libMCell_wrap.o
	rm -f _libMCell.so
	rm -f mcell_main.o
	rm -f mcell_main

