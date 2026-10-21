CFLAGS = -g -Wall -Wextra -pedantic -Wno-unused-parameter      

CC = gcc

PROGRAMS = main

.PHONY: all clean

all: $(PROGRAMS)

main : main.o temp_ccl_rech.o entreeSortieH.o entreeSortieLC.o biblioLC.o biblioH.o 
	$(CC) -o $@ $(CFLAGS) $^

main.o : main.c
	gcc $(CFLAGS) -c main.c

temp_ccl_rech.o : temp_ccl_rech.c
	gcc $(CFLAGS) -c temp_ccl_rech.c

entreeSortieH.o : entreeSortieH.c
	gcc $(CFLAGS) -c entreeSortieH.c

entreeSortieLC.o : entreeSortieLC.c
	gcc $(CFLAGS) -c entreeSortieLC.c

biblioH.o : biblioH.c
	gcc $(CFLAGS) -c biblioH.c

biblioLC.o : biblioLC.c
	gcc $(CFLAGS) -c biblioLC.c

clean:
	rm -f *.o *~ $(PROGRAMS)
