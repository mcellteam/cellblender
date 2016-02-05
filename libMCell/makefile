PYTHON_INCLUDE = /usr/include/python3.4m

all: mcell_main

mcell_main: mcell_main.c libMCell.c libMCell.h libMCell.i JSON.o makefile
	gcc -c mcell_main.c libMCell.c
	gcc -lm -o mcell_main mcell_main.o libMCell.o JSON.o
	swig -python libMCell.i
	gcc -c libMCell.c libMCell_wrap.c -fPIC -I$(PYTHON_INCLUDE)
	ld -lm -shared libMCell.o libMCell_wrap.o JSON.o -o _libMCell.so

JSON.o: JSON.c JSON.h makefile
	gcc -o JSON.o -c JSON.c -fPIC -I$(PYTHON_INCLUDE)

clean:
	rm -f libMCell.o
	rm -f libMCell.py
	rm -f libMCell_wrap.c
	rm -f libMCell_wrap.o
	rm -f _libMCell.so
	rm -f mcell_main.o
	rm -f JSON.o
	rm -f mcell_main
	rm -f *.pyc


test_c: mcell_main
	./mcell_main

test_py: mcell_python.py mcell_main
	python3 mcell_python.py data_model=dm.txt


