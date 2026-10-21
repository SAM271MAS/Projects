#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "Chaine.h"
#include "Reseau.h"
#include "Hachage.h"
#include "ArbreQuat.h"

int main(int argc, char **argv){

    if(argc != 3){
        printf("Erreur : utilisation incorrecte. Voici un exemple d'utilisation :\n%s <nom_du_fichier.cha> <nb_méthode>\n ou nb_méthode est un entier compris entre un et trois pour (liste, table de hachage, arbre)\n",argv[0]);
        return EXIT_FAILURE;
    }
    FILE *f = fopen(argv[1], "r");
    assert(f);
    Chaines *C = lectureChaines(f);
    fclose(f);

    int choix = atoi(argv[2]);
    Reseau *R;
    if(choix == 1){
        R = reconstitueReseauListe(C);
        FILE *f2 = fopen("ReseauListe.res", "w");
        ecrireReseau(R, f2);
        fclose(f2);
        afficheReseauSVG(R, "ReseauListe");
    }
    else if(choix == 2){
        R = reconstitueReseauHachage(C, C->nbChaines*10);
        FILE *f2 = fopen("ReseauHach.res", "w");
        ecrireReseau(R, f2);
        fclose(f2);
        afficheReseauSVG(R, "ReseauHach");
    }
    else if(choix == 3){
        R = reconstitueReseauArbre(C);
        FILE *f2 = fopen("ReseauArbre.res", "w");
        ecrireReseau(R, f2);
        fclose(f2);
        afficheReseauSVG(R, "ReseauArbre");
    }
    else{
        printf("Erreur : utilisation incorrecte. Voici un exemple d'utilisation :\n%s <nom_du_fichier.h> <nb_méthode>\n ou nb_méthode est un entier compris entre un et trois pour (liste, table de hachage, arbre)\n",argv[0]);
        libererChaines(C);
        return EXIT_FAILURE;

    }
    libererChaines(C);
    libererReseau(R);
    return EXIT_SUCCESS;
    
}
