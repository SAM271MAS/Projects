#include <assert.h>      
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "ecosys.h"

float p_ch_dir=0.01;
float p_reproduce_proie=0.4;
float p_reproduce_predateur=0.5;
int temps_repousse_herbe=-15;


int main(void) {
    /* Part 1, exercice 6, question 3 */
    Animal *liste_proie = NULL;
    Animal *liste_predateur = NULL;
    float energie=10;

    srand(time(NULL));

    for(int i = 0; i < 20; i++){

        int x, y;

        //créer 20 prédateurs
        x = (rand() % (SIZE_X));
        y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_predateur);

        // pour tester la fonction enlever_animal
        // if (i % 2 == 0){
        //     enlever_animal(&liste_predateur, liste_predateur);
        // }

        //créer 20 proies
        x = (rand() % (SIZE_X));
        y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_proie);

        // pour tester la fonction enlever_animal
        // if (i % 2 == 0){
        //     enlever_animal(&liste_proie, liste_proie);
        // }

    }
    afficher_ecosys(liste_proie,liste_predateur);      
    
    /* Part 2, exercice 3, question 1 */
    ecrire_ecosys("ecrit.txt", liste_predateur, liste_proie);


    /* Part 1, exercice 6, question 5 */
    liste_predateur = liberer_liste_animaux(liste_predateur);
    liste_proie = liberer_liste_animaux(liste_proie);


    /* Part 2, exercice 3, question 1 */
    lire_ecosys("ecrit.txt", &liste_predateur, &liste_proie);
    ecrire_ecosys("lire.txt", liste_predateur, liste_proie);

    afficher_ecosys(liste_proie,liste_predateur);      

    liste_predateur = liberer_liste_animaux(liste_predateur);
    liste_proie = liberer_liste_animaux(liste_proie);


    return 0;


}
