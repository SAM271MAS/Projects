#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Chaine.h"

// test des fonctions : lectureChaines, ecrireChaines, libererChaines
int main(int argc, char *argv[]){
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    FILE *f2 = fopen("test_ecr_cha.txt", "w");
    assert(f2);
    ecrireChaines(c,f2);
    fclose(f2);

    afficheChainesSVG(c, "ChaineLect");

    libererChaines(c);
    
    //
    // gcc -I.. ../Chaine.c ../SVGwriter.c ex1.c -o ex1 -lm && valgrind ./ex1
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
