#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ecosys.h"

/* PARTIE 1*/
/* Fourni: Part 1, exercice 4, question 2 */
Animal *creer_animal(int x, int y, float energie) {
    //créer un animal alloué dynamiquement et renvoie son pointeur

    Animal *na = (Animal *)malloc(sizeof(Animal));
    assert(na);

    na->x = x;
    na->y = y;
    na->energie = energie;
    na->dir[0] = rand() % 3 - 1;
    na->dir[1] = rand() % 3 - 1;
    na->suivant = NULL;

    return na;
}

/* Fourni: Part 1, exercice 4, question 3 */
Animal *ajouter_en_tete_animal(Animal *liste, Animal *animal) {
    //prendre un animal et une liste et mettre l'animal en tête de la liste
    //renvoie l'adresse de l'animal (la première de la liste)

    assert(animal);
    assert(!animal->suivant);
    animal->suivant = liste;

    return animal;
}

/* A faire. Part 1, exercice 6, question 2 */
void ajouter_animal(int x, int y,  float energie, Animal **liste_animal) {
    //créer un animal et le mettre en tête de la liste

    assert((x >= 0) && (x < SIZE_X));
    assert((y >= 0) && (y < SIZE_Y));

    Animal *a = creer_animal(x, y, energie);
    assert(a != NULL);

    *liste_animal = ajouter_en_tete_animal(*liste_animal, a);
}

/* A Faire. Part 1, exercice 6, question 4 */
Animal* liberer_liste_animaux(Animal *liste) {
    //désallouer une liste non vide
    //renvoie NULL

    assert(liste);

    while (liste){
        Animal *tmp = liste -> suivant ;
        free(liste);
        liste = tmp;
    }

    return NULL;
}

/* A Faire. Part 1, exercice 6, question 7 */
void enlever_animal(Animal **liste, Animal *animal) {
    //désallouer de la liste l'animal passé dans les arguments

    assert(animal);

    Animal *tmp = *liste;
    Animal *precedent = NULL;

    //si animal en tête de liste
    if (tmp == animal) {
        *liste = (*liste)->suivant;
        free(animal);
        return;
    }

    while (tmp && tmp != animal) {
        precedent = tmp;
        tmp = tmp->suivant;
    }

    //si l'animal n'est pas trouvé
    if (tmp == NULL) {
        return;
    }

    precedent->suivant = tmp->suivant;
    free(tmp);
}


/* Fourni: part 1, exercice 4, question 4 */
unsigned int compte_animal_rec(Animal *la) {
    if (!la) return 0;
    return 1 + compte_animal_rec(la->suivant);
}

/* Fourni: part 1, exercice 4, question 4 */
unsigned int compte_animal_it(Animal *la) {
    int cpt=0;
    while (la) {
      ++cpt;
      la=la->suivant;
    }
    return cpt;
}



/* Part 1. Exercice 5, question 1, ATTENTION, ce code est susceptible de contenir des erreurs... */
void afficher_ecosys(Animal *liste_proie, Animal *liste_predateur) {
    unsigned int i, j;
    char ecosys[SIZE_X][SIZE_Y];
    Animal *pa=NULL;

    /* on initialise le tableau */
    for (i = 0; i < SIZE_X; ++i) {
      for (j = 0; j < SIZE_Y; ++j) {
        ecosys[i][j]=' ';
      }
    }

    /* on ajoute les proies */
    pa = liste_proie;
    while (pa) {
      ecosys[pa->x][pa->y] = '*';
      pa=pa->suivant;
    }

    /* on ajoute les predateurs */
    pa = liste_predateur; while (pa) { if ((ecosys[pa->x][pa->y] == '@') || (ecosys[pa->x][pa->y] == '*')) { /* proies aussi present */ ecosys[pa->x][pa->y] = '@';
        } else {
          ecosys[pa->x][pa->y] = 'O';
        }
      pa = pa->suivant;
    }

    /* on affiche le tableau */
    printf("+");
    for (j = 0; j < SIZE_Y; ++j) {
      printf("-");
    }
    printf("+\n");
    for (i = 0; i < SIZE_X; ++i) {
      printf("|");
      for (j = 0; j < SIZE_Y; ++j) {
        putchar(ecosys[i][j]);
      }
      printf("|\n");
    }
    printf("+");
    for (j = 0; j<SIZE_Y; ++j) {
      printf("-");
    }
    printf("+\n");
    int nbproie=compte_animal_it(liste_proie);
    int nbpred=compte_animal_it(liste_predateur);

    printf("Nb proies : %5d\tNb predateurs : %5d\n", nbproie, nbpred);

}


void clear_screen() {
  printf("\x1b[2J\x1b[1;1H");  /* code ANSI X3.4 pour effacer l'ecran */
}


/* PART 2 */

/* part 2, exercice 1, question 1 */
void ecrire_ecosys(const char *nom_fichier, Animal* liste_predateur, Animal* liste_proie){
    //écrire dans un fichier les listes de proies et de prédateurs

    Animal *tmp;
    FILE *f = fopen(nom_fichier,"w");
    assert(f);

    //liste proies
    tmp=liste_proie;
    fprintf(f, "<proies>\n");
    while (tmp) {
        fprintf(f,"x=%d y=%d dir=[%d %d] e=%f\n",tmp->x, tmp->y, tmp->dir[0], tmp->dir[1], tmp->energie);
        tmp=tmp->suivant;
    }
    fprintf(f,"</proies>\n");

    //liste prédateurs
    tmp=liste_predateur;
    fprintf(f,"<predateurs>\n");
    while (tmp) { // écrit chaque predateur dans le fichier
        fprintf(f,"x=%d y=%d dir=[%d %d] e=%f\n",tmp->x, tmp->y, tmp->dir[0], tmp->dir[1], tmp->energie);
        tmp=tmp->suivant;
    }
    fprintf(f, "</predateurs>\n");

    fclose(f);
}

/* part 2, exercice 1, question 2 */
void lire_ecosys(const char *nom_fichier, Animal** liste_predateur, Animal** liste_proie){
    //lit à partir d'un fichier une liste de proies et une liste de prédateurs et les crée

    char buffer[256];
    int x, y, dir[2];
    float energie;
    FILE * f = fopen(nom_fichier, "r");
    assert(f);

    // si erreur de format
    if((fgets(buffer,256, f)==NULL)||(strcmp(buffer, "<proies>\n")!=0)){
        printf("Erreur format\n");
        exit(-1);
    }

    //liste proies
    while((fgets(buffer, 256, f)!=NULL)&&(strcmp(buffer, "</proies>\n")!=0)){
        int n = sscanf(buffer, "x=%d y=%d dir=[%d %d] e=%f\n", &x, &y, &dir[0], &dir[1], &energie);
        assert(n==5);
        ajouter_animal(x, y, energie, liste_proie);
        (*liste_proie) -> dir[0] = dir[0];
        (*liste_proie) -> dir[1] = dir[1];
    }

    //si erreur de format
    if((fgets(buffer,256, f)==NULL)||(strcmp(buffer, "<predateurs>\n")!=0))
        exit(-1);

    //liste prédateurs
    while((fgets(buffer,256, f)!=NULL)&&(strcmp(buffer, "</predateurs>\n")!=0)){
        int n = sscanf(buffer, "x=%d y=%d dir=[%d %d] e=%f\n", &x, &y, &dir[0], &dir[1], &energie);
        assert(n==5);
        ajouter_animal(x, y, energie, liste_predateur);// est que les dir sont les même?
        (*liste_proie) -> dir[0] = dir[0];
        (*liste_proie) -> dir[1] = dir[1];
    }

    fclose(f);
}

/* Part 2. Exercice 2, question 1 */
void bouger_animaux(Animal *la) {
    //déplacer tous les animaux dans leur direction
    //certains animaux peuvent changer de direction selon la probabilité p_ch_dir

    Animal *tmp = la;

    while (tmp) {
        
        // changement de direction 
        if (rand() / (float)RAND_MAX < p_ch_dir) {  
            tmp -> dir[0] = (rand() % 3) - 1;
            tmp -> dir[1] = (rand() % 3) - 1;
        }

        tmp ->x = (tmp ->x + SIZE_X - tmp -> dir[0]) % SIZE_X; 
        tmp ->y = (tmp ->y + SIZE_Y - tmp -> dir[1]) % SIZE_Y; 
        tmp = tmp->suivant;
    }

}

/* Part 2. Exercice 2, question 2 */
void reproduce(Animal **liste_animal, float p_reproduce) {
    //en suivant la probabilité passée en argument pour chaque animal crée un nouvel animal

    Animal *tmp = *liste_animal;

    while(tmp){
        if (rand()/ (float)RAND_MAX < p_reproduce){
            tmp -> energie /= 2.0;
            ajouter_animal(tmp -> x, tmp -> y,  tmp -> energie, liste_animal);
        // est que les dir sont les même?
        }
        tmp = tmp -> suivant;
    }
}


/* Part 2. Exercice 5, question 1 */
void rafraichir_proies(Animal **liste_proie, int monde[SIZE_X][SIZE_Y]) {
    //fonction de gestion des proies

    //bouger les proies
    bouger_animaux(*liste_proie);

    Animal *tmp = *liste_proie;
    Animal *next;

    while (tmp){

        //baisser l'énergie de 1
        tmp -> energie--;

        //supprimer les proies dont l’énergie est inférieure ou égal à 0
        if ((tmp -> energie) <= 0){
            next = tmp->suivant;
            enlever_animal(liste_proie, tmp);
            tmp = next;
            continue;
        }

        /* Part 2. Exercice 7, question 3 */
        if(monde[tmp -> x][tmp -> y] > 0){
            tmp -> energie += monde[tmp -> x][tmp -> y];
            monde[tmp -> x][tmp -> y] = temps_repousse_herbe;
        }

        tmp = tmp->suivant;

    }

    reproduce(liste_proie, p_reproduce_proie);

}



/* Part 2. Exercice 6, question 1 */
Animal *animal_en_XY(Animal *l, int x, int y) {
    //vérifier si une proie est dans le cas. 
    //si oui renvoie l'adresse de la proie 
    //sinon renvoie null

    Animal *tmp = l;

    while (tmp){
        if (tmp -> x == x && tmp -> y == y)
            return tmp;
        tmp = tmp->suivant;
    }
    return NULL;

}

/* Part 2. Exercice 6, question 2 */
void rafraichir_predateurs(Animal **liste_predateur, Animal **liste_proie) {
    //fonction de gestion des prédateurs

    bouger_animaux(*liste_predateur);

    Animal *tmp = *liste_predateur;
    Animal *next;
    Animal *exist;

    while (tmp){

        //baisser l'énergie de 1
        tmp -> energie--;

        //supprimer les prédateurs dont l’énergie est inférieure ou égal à 0
        if ((tmp -> energie) <= 0){
            next = tmp -> suivant;
            enlever_animal(liste_predateur, tmp);
            tmp = next;
            continue;
        }

        //si une proie est dans le même cas que le prédateur 
        //enlever la proie et donner son énergie au prédateur
        exist = animal_en_XY(*liste_proie, tmp -> x, tmp -> y);
        if (exist){
            tmp -> energie += exist -> energie;
            enlever_animal(liste_proie, exist);
        }

        tmp = tmp->suivant;
    }
    reproduce(liste_predateur, p_reproduce_predateur);
}


/* Part 2. Exercice 7, question 2 */
void rafraichir_monde(int monde[SIZE_X][SIZE_Y]){
    //incrémenter de 1 la quantité d'herbe

    int i, j;

    for (i = 0; i < SIZE_X; i++){
        for (j = 0; j < SIZE_Y; j++){
            monde[i][j] += 1;
        }
    }
}

