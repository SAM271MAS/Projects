#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "biblioH.h"

BiblioH* charger_n_entreesH(char* nomfic, int n, int nb_case){
    /* Charge les 'n' premières entrées d'un fichier dans une bibliothèque de hachage. 
   Le fichier doit contenir des livres sous la forme 'num titre auteur'. */
    
    BiblioH *b = creer_biblioH(nb_case);

    int num;
    char *titre = (char *)malloc(100 * sizeof(char));
    char *auteur = (char *)malloc(100 * sizeof(char));
    char *buffer = (char *)malloc(256 * sizeof(char));
    FILE *f = fopen(nomfic, "r");
    assert(f);

    while(n != 0){
        fgets(buffer, 256, f);
        sscanf(buffer, "%d %s %s", &num, titre, auteur);
        inserer(b, num, titre, auteur);
        n--;
    }
    free(buffer);
    free(titre);
    free(auteur);

    fclose(f);

    return b;
    

}

void enregistrer_biblioH(BiblioH *b, char* nomfic){
    /* Enregistre tous les livres d'une bibliothèque de hachage dans un fichier. 
   Chaque livre est enregistré sous la forme 'clef num titre auteur'. */

    if (!b)
        return;

    FILE *f = fopen(nomfic,"w");
    assert(f);

    LivreH *l;

    for (int i = 0; i < b->m; i++){                                                          
        l = b->T[i];

        while (l){
            fprintf(f, "%d %d %s %s\n", l->clef, l->num, l->titre, l->auteur);
            l = l->suiv;
        }
    }
    fclose(f);
}

