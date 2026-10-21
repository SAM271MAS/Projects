#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Reseau.h"
#include "../Hachage.h"

// test des fonctions :reconstitueReseauHachage
int main(int argc, char *argv[]){

    // 4.1 test de la fonction clef
    // for(int x = 0; x <= 10; x++){
    //     for(int y = 0; y <= 10; y++){
    //         printf("x : %d, y : %d clef = %f ",x ,y, clef_hachage(x,  y));
    //     }
    //     printf("\n");
    // }
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    Reseau *R = reconstitueReseauHachage(c, 30);

    FILE *f2 = fopen("test_res_hach.txt", "w");
    assert(f2);
    ecrireReseau(R, f2);
    fclose(f2);
    afficheReseauSVG(R, "ReseauHachage");

    libererReseau(R);

    libererChaines(c);

    //
    // gcc -I.. ../Hachage.c ../Reseau.c ../Chaine.c ../SVGwriter.c ex4.c -o ex4 -lm && valgrind ./ex4
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
