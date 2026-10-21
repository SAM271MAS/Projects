CFLAGS = -g -Wall -Wextra -pedantic -Wno-unused-parameter
CC = gcc
PROGRAMS = ReconstitueReseau Stats_main

.PHONY: all clean

all: $(PROGRAMS)


Stats_main : Stats_main.o ArbreQuat.o Hachage.o Reseau.o Chaine.o SVGwriter.o
	$(CC) $(CFLAGS) -o $@ $^ -lm

ReconstitueReseau : ReconstitueReseau.o ArbreQuat.o Hachage.o Reseau.o Chaine.o SVGwriter.o
	$(CC) $(CFLAGS) -o $@ $^ -lm

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o *~ $(PROGRAMS)

