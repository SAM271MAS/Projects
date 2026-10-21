#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Reseau.h"

// test des fonctions : reconstitueReseauListe, libererReseau
int main(int argc, char *argv[]){
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    Reseau *R = reconstitueReseauListe(c);
    libererReseau(R);

    libererChaines(c);
    
    //
    // gcc -I.. ../Reseau.c ../Chaine.c ../SVGwriter.c ex2.c -o ex2 -lm && valgrind ./ex2
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
