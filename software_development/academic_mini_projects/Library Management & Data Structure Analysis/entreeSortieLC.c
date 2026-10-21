#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "biblioLC.h"


Biblio* charger_n_entrees(char* nomfic, int n){
    /* Charge les 'n' premières entrées d'un fichier dans une bibliothèque. 
   Le fichier doit contenir des livres sous la forme 'num titre auteur'. */
    
    Biblio *b = creer_biblio();

    int num;
    char *titre = (char *)malloc(100 * sizeof(char));
    char *auteur = (char *)malloc(100 * sizeof(char));
    char *buffer = (char *)malloc(256 * sizeof(char));
    FILE *f = fopen(nomfic, "r");
    assert(f);

    while(n != 0){
        fgets(buffer, 256, f);
        sscanf(buffer, "%d %s %s", &num, titre, auteur);
        inserer_en_tete(b, num, titre, auteur);
        n--;
    }
    free(buffer);
    free(titre);
    free(auteur);

    fclose(f);

    return b;
}

void enregistrer_biblio(Biblio *b, char* nomfic){
    /* Enregistre tous les livres d'une bibliothèque dans un fichier. 
   Chaque livre est enregistré sous la forme 'num titre auteur'. */

    Livre *l = b->L;

    FILE *f = fopen(nomfic,"w");
    assert(f);

    while (l){
        fprintf(f, "%d %s %s\n", l->num, l->titre, l->auteur);
        l = l->suiv;
    }

    fclose(f);
}

