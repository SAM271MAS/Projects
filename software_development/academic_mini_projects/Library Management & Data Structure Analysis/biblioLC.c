#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "biblioLC.h"

Livre* creer_livre(int num,char* titre,char* auteur){
    /* Crée un nouveau livre avec le numéro, le titre et l'auteur spécifiés */
    Livre *l = (Livre *)malloc(sizeof(Livre));
    assert(l);
    l->num = num;
    l->titre = strdup(titre);
    l->auteur = strdup(auteur);
    l->suiv = NULL;
    return l;
}

void liberer_livre(Livre* l){
    /* Libère la mémoire allouée à un livre */
    if (!l)
        return;
    free(l->titre);
    free(l->auteur);
    free(l);
}

Biblio* creer_biblio(){
    /* Crée une nouvelle bibliothèque vide */
    Biblio *b = (Biblio *)malloc(sizeof(Biblio));
    assert(b);
    b->L = NULL;
    b->num_livre = 0;
    return b;
}

void liberer_biblio(Biblio* b){
    /* Libère la mémoire allouée à une bibliothèque */
    if (!b)
        return;
    Livre *tmp;
    while(b->L){
        tmp = b->L;
        b -> L = tmp -> suiv;
        liberer_livre(tmp);
    }
    free(b);
}

void inserer_en_tete(Biblio* b,int num,char* titre,char* auteur){
    /* Insère un nouveau livre en tête de la bibliothèque */
    if (!b)
        return;
    Livre *l = creer_livre(num, titre, auteur);
    l->suiv = b->L;
    b->L = l;
    b->num_livre++;
}

void afficher_livre(Livre *l){
    /* Affiche les détails d'un livre */
    if (l)
        printf("num livre: %d\ntitre : %s\nauteur : %s\n", l->num, l->titre, l->auteur);
}

void afficher_bib(Biblio *b){
    /* Affiche tous les livres dans la bibliothèque */
    if (!b)
        return;

    Livre *l = b->L;
    printf("nombre total de livres : %d\n\n", b->num_livre);
    while(l){
        afficher_livre(l);
        printf("\n");
        l = l->suiv;
    }
}

Livre *recherche_num(Biblio *b, int n){
    /* Recherche un livre par son numéro dans la bibliothèque */
    if (!b)
        return NULL;
    Livre *l = b->L;
    while(l){
        if (l->num == n)
            return l;
        l = l->suiv;
    }
    printf("le livre du numéro\033[31m %d \033[0mn'est pas la bibliothèque\n", n);
    return NULL;

}

Livre *recherche_titre(Biblio *b, char *t){
    /* Recherche un livre par son titre dans la bibliothèque */
    if (!b)
        return NULL;

    Livre *l = b->L;
    while(l){
        if (strcmp(l->titre, t) == 0)
            return l;
        l = l->suiv;
    }
    printf("le livre de titre\033[31m %s \033[0mn'est pas la bibliothèque\n", t);
    return NULL;

}

Biblio *recherche_auteur(Biblio *b, char *a){
    /* Recherche tous les livres d'un auteur dans la bibliothèque */
    if (!b)
        return NULL;

    Livre *l = b->L;
    Biblio *b_auteur = creer_biblio();
    while(l){
        if (strcmp(l->auteur, a) == 0)
            inserer_en_tete(b_auteur, l->num, l->titre, l->auteur);
        l = l->suiv;
    }
    if (b_auteur->num_livre != 0)
        return b_auteur;

    printf("l'auteur\033[31m %s \033[0mn'a aucun livre dans cette bibliothèque\n", a);
    liberer_biblio(b_auteur);
    return NULL;

}

void supprimer_ouvrage(Biblio *b, int n, char *a, char *t){
    /* Supprime un ouvrage de la bibliothèque */
    Livre *l = b->L;
    Livre *prec = NULL;
    while(l && (l->num != n || strcmp(l->auteur, a) != 0 || strcmp(l->titre, t) != 0)){
        prec = l;
        l = l->suiv;
    }
    if(!l){
        printf("le livre n'est pas dans la bibliothèque la suppression est annulée\n");
        return;
    }
    if(!prec){
        b->L = l->suiv;
        b->num_livre--;
        liberer_livre(l);
        return;
    }
    prec->suiv = l->suiv;
    b->num_livre--;
    liberer_livre(l);

}

void fusion_bib(Biblio *b1, Biblio *b2){
    /* Fusionne deux bibliothèques, supprime et désalloue la deuxième bibliothèque*/
    Livre *l = b2->L;

    while(l){
        inserer_en_tete(b1, l->num, l->titre, l->auteur);
        l = l->suiv;
    }
    liberer_biblio(b2);

}

Biblio *ouvrages_plusieurs_exemplaires(Biblio *b){
    /* Retourne une bibliothèque contenant les ouvrages ayant plusieurs exemplaires.
   Utilise 'break' pour éviter l'ajout répété du même livre dans la nouvelle bibliothèque. 
   il peut toujours y avoir des répétitions dans b_rep si un livre a plus de deux exemplaires 
   Chaque paire d’exemplaires du même livre sera ajoutée à b_rep*/
    Biblio *b_rep = creer_biblio();
    Livre *l1, *l2;
    l1 = b->L;
    while(l1){
        l2 = l1->suiv;
        while(l2){
            if(strcmp(l1->auteur, l2->auteur) == 0 && strcmp(l1->titre, l2->titre) == 0){
                inserer_en_tete(b_rep, l1->num, l1->titre, l1->auteur);
                inserer_en_tete(b_rep, l2->num, l2->titre, l2->auteur);
                break;
            }
            l2 = l2->suiv;
        }
        l1 = l1->suiv;
    }
    if (b_rep->num_livre != 0)
        return b_rep;
    liberer_biblio(b_rep);
    return NULL;
}
