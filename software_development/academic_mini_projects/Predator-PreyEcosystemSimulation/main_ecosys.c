#include <assert.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <strings.h>

#include "ecosys.h"



#define NB_PROIES 20
#define NB_PREDATEURS 20
#define T_WAIT 40000


/* Parametres globaux de l'ecosysteme (externes dans le ecosys.h)*/
float p_ch_dir = 0.01;
float p_reproduce_proie = 0.4;
float p_reproduce_predateur = 0.5;
int temps_repousse_herbe = -15;


int main(void) {

    srand(time(NULL));

    Animal *liste_proie = NULL;
    Animal *liste_predateur = NULL;
    float energie = 20.0;
    int i;
    int monde[SIZE_X][SIZE_Y];

    //Part 2, exercice 7, question 1 
    for (i = 0; i < SIZE_X; i++){
        for (int j = 0; j < SIZE_Y; j++){
            monde[i][j] = 0;
        }
    }

   /*
    //Part 2, exercice 4, question 1 

    Animal *a = creer_animal(0, 0, 10.);
    a->dir[0] = 1;
    a->dir[1] = 1;
    a->suivant = NULL;
    afficher_ecosys(a,NULL);
    bouger_animaux(a);
    afficher_ecosys(a,NULL);

     //Part 2, exercice 4, question 1
     
    reproduce(&a, 1);
    afficher_ecosys(a,NULL);
    liberer_liste_animaux(a);

    */



   /*
    // Part 2, exercice 5, question 2

    //créer 20 proies
    for(i = 0; i < NB_PROIES; i++){
        int x = (rand() % (SIZE_X));
        int y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_proie);
    }

    i = 0;
    //boucle pour essayer la fonction rafraichir_proie
    while (i < 200 && compte_animal_it(liste_proie) != 0){
        afficher_ecosys(liste_proie, liste_predateur);      
        rafraichir_proies(&liste_proie, monde) ;
        usleep(1000000);
        clear_screen();
        i++;
    }


    */



   /*
    // Part 2, exercice 6, question 3

    //créer 20 proies
    for(i = 0; i < NB_PROIES; i++){
        int x = (rand() % (SIZE_X));
        int y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_proie);
    }

    //créer 20 predateurs
    for(i = 0; i < NB_PREDATEURS; i++){
        int x = (rand() % (SIZE_X));
        int y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_predateur);
    }


    i = 0;
    //boucle pour essayer la fonction rafraichir_proie
    //et la fonction rafraichir_predateurs
    while (i < 200 && compte_animal_it(liste_proie) != 0){
        afficher_ecosys(liste_proie, liste_predateur);      
        rafraichir_proies(&liste_proie, monde) ;
        rafraichir_predateurs(&liste_predateur, &liste_proie);
        usleep(1000000);
        clear_screen();
        i++;
    }

    */


    // Part 2, exercice 8
    FILE *f = fopen("Evol_Pop.txt", "w");
    assert(f);
   
    //créer 20 proies
    for(i = 0; i < NB_PROIES; i++){
        int x = (rand() % (SIZE_X));
        int y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, energie, &liste_proie);
    }

    //créer 20 predateurs
    for(i = 0; i < NB_PREDATEURS; i++){
        int x = (rand() % (SIZE_X));
        int y = (rand() % (SIZE_Y));
        ajouter_animal(x, y, 20, &liste_predateur);
    }

    afficher_ecosys(liste_proie, liste_predateur);      

    i = 0;
    while (i < 500 && compte_animal_it(liste_proie) != 0 && compte_animal_it(liste_predateur) != 0){
        // écrire dans le fichier l’indice de l’itération, le nombre de proies, le nombre de prédateurs
        fprintf(f,"%d %d %d\n", i, compte_animal_it(liste_proie), compte_animal_it(liste_predateur));

        rafraichir_proies(&liste_proie, monde) ;
        rafraichir_predateurs(&liste_predateur, &liste_proie);
        rafraichir_monde(monde);

        afficher_ecosys(liste_proie, liste_predateur);      

        // faire une pause d'1 seconde
        //usleep(1000000);
        clear_screen();
        i++;
    }
    fclose(f);
    
    if(liste_proie){
	   liberer_liste_animaux(liste_proie);
    }

    if(liste_predateur){
	    liberer_liste_animaux(liste_predateur);
    }


  return 0;
}

