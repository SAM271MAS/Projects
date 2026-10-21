#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Reseau.h"
#include "../ArbreQuat.h"

// test des fonctions :reconstitueReseauArbre
int main(int argc, char *argv[]){
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    Reseau *R = reconstitueReseauArbre(c);
    //Pour visualiser l'arbre on peut décommenter la ligne printArbreQuat(a); à la fin de la fonction reconstitueReseauArbre

    FILE *f2 = fopen("test_res_Arb.txt", "w");
    assert(f2);
    ecrireReseau(R, f2);
    fclose(f2);
    afficheReseauSVG(R, "ReseauArbre");

    libererReseau(R);

    libererChaines(c);
    
    //
    // gcc -I.. ../ArbreQuat.c ../Reseau.c ../Chaine.c ../SVGwriter.c ex5.c -o ex5 -lm && valgrind ./ex5
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
