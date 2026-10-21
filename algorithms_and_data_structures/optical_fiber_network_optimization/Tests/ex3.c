#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Reseau.h"

// test des fonctions : ecrireReseau
int main(int argc, char *argv[]){
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    Reseau *R = reconstitueReseauListe(c);

    FILE *f2 = fopen("test_res_liste.txt", "w");
    assert(f2);
    ecrireReseau(R, f2);
    fclose(f2);
    afficheReseauSVG(R, "ReseauListe");

    libererReseau(R);

    libererChaines(c);
    
    //
    // gcc -I.. ../Reseau.c ../Chaine.c ../SVGwriter.c ex3.c -o ex3 -lm && valgrind ./ex3
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
