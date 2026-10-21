#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "../Reseau.h"
#include "../Hachage.h"
#include "../Graphe.h"

// test des fonctions : creerGraphe, reorganiseReseau, libererGraphe
int main(int argc, char *argv[]){
    
    FILE *f = fopen("00014_burma.cha", "r");
    assert(f);
    Chaines *c = lectureChaines(f);
    fclose(f);

    Reseau *R = reconstitueReseauHachage(c, 30);


    Graphe *G = creerGraphe(R);
    printGraphe(G);

    int nb_aretes = 0;
    int *tab = BFS(G, 1, 12, &nb_aretes);
    if (tab) {
        for(int i = 0; i <= nb_aretes; i++) {
            printf("%d ", tab[i]);
        }
        printf("\n");
        free(tab);
    }
    printf("inférieur à γ ? %d\n", reorganiseReseau(R));


    libererReseau(R);

    libererChaines(c);
    libererGraphe(G);
    
    //
    // gcc -I.. ../Graphe.c ../Struct_File.c ../Hachage.c ../Reseau.c ../Chaine.c ../SVGwriter.c ex7.c -o ex7 -lm && valgrind ./ex7
    // En tapant les commandes ci-dessus, nous pouvons vérifier nos fonctions
    return EXIT_SUCCESS;
}
