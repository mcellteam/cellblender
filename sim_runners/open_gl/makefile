SimControl: SimControl.o
	-gcc -o SimControl SimControl.o -lGL -lglut -lGLU

SimControl.o: SimControl.c
	-gcc -c -std=c99 -I/usr/include/GL SimControl.c

.PHONY: clean
clean:
	-rm -f SimControl.o
	-rm -f SimControl

