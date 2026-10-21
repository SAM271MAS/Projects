#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <math.h>
#include "biblioH.h"

int fonctionClef(char* auteur){
    /* Calcule la somme des valeurs ASCII des caractères d'un auteur. 
     * Cette somme est utilisée comme clé pour le hachage. */
    int len = strlen(auteur), somme = 0;
    for (int i = 0; i < len; i++){
        somme += auteur[i];
    }
    return somme;
}

LivreH* creer_livreH(int num,char* titre,char* auteur){
    /* Crée un nouveau livre avec un numéro, un titre et un auteur donnés. 
     * La clé du livre est calculée à partir du nom de l'auteur. */
    LivreH *l = (LivreH *)malloc(sizeof(LivreH));
    assert(l);
    l->clef = fonctionClef(auteur);
    l->num = num;
    l->titre = strdup(titre);
    l->auteur = strdup(auteur);
    l->suiv = NULL;
    return l;
}
void liberer_livreH(LivreH* l){
    /* Libère la mémoire allouée à un livre. 
     * Cela comprend le titre, l'auteur et la structure du livre elle-même. */
    if (!l)
        return;
    free(l->titre);
    free(l->auteur);
    free(l);
}


BiblioH* creer_biblioH(int m){
    /* Crée une nouvelle bibliothèque avec une taille donnée. 
     * La bibliothèque est représentée par une table de hachage de taille 'm', 
     * où chaque cas est initialisée à NULL. */
    BiblioH* b = malloc(sizeof(BiblioH));
    assert(b);

    b->T = malloc(m * sizeof(LivreH*));
    assert(b->T);

    for (int i = 0; i < m; i++){
        b->T[i] = NULL;
    }

    b->nE = 0;
    b->m = m;
    return b;
}

void liberer_biblioH(BiblioH* b){
    /* Libère la mémoire allouée à une bibliothèque. 
     * Cela comprend la libération de tous les livres dans la bibliothèque et la table de hachage elle-même. */
    if (!b)
        return;

    LivreH *l;
    LivreH *tmp;

    for (int i = 0; i < b->m; i++){
        l = b->T[i];

        while (l){
            tmp = l;
            l = l->suiv;
            liberer_livreH(tmp);
        }
    }
    free(b->T);
    free(b);
}

int fonctionHachage(int cle, int m){
    
/* Calcule la valeur de hachage d'une clé donnée.*/
    double A = (sqrt(5)-1)/2;
    return (int)(m*((cle * A) - (int)(cle * A)));
}

void inserer(BiblioH* b,int num,char* titre,char* auteur){
    /* Insère un nouveau livre dans la bibliothèque. 
     * Le livre est inséré à la position calculée par la fonction de hachage. 
     * Si la position est déjà occupée, le livre est ajouté au début de la liste chaînée à cette position. */
    LivreH *lh = creer_livreH(num, titre,auteur);
    int pos = fonctionHachage(lh->clef, b->m);

    lh->suiv = b->T[pos];
    b->T[pos] = lh;
    b->nE++;

}
void afficher_livreH(LivreH *l){
    /* Affiche les détails d'un livre.*/
    if (l)
        printf("clef livre: %d\nnum livre: %d\ntitre : %s\nauteur : %s\n", l->clef, l->num, l->titre, l->auteur);
}                                                                                            

void afficher_bibH(BiblioH *b){
    /* Affiche tous les livres de la bibliothèque. 
     * Pour chaque position de la table de hachage, tous les livres de la liste chaînée à cette position sont affichés. */
    if (!b)
        return;

    LivreH *l;
    printf("nombre total de livres : %d\n\n", b->nE);

    for (int i = 0; i < b->m; i++){                                                          
        l = b->T[i];
        printf("case[%d]\n",i);

        while (l){
            afficher_livreH(l);                                                                   
            printf("\n");
            l = l->suiv;
        }
    }
}

LivreH *recherche_numH(BiblioH *b, int n){
    /* Recherche un livre dans la bibliothèque par son numéro. 
     * La recherche est effectuée en parcourant toutes les listes chaînées de la table de hachage. */
    if (!b)
        return NULL;

    LivreH *l;

    for (int i = 0; i < b->m; i++){                                                          
        l = b->T[i];
        while (l){
            if (l->num == n){
                printf("le livre est dans la case [%d]\n", i);
                return l;
            }
            l = l->suiv;
        }
    }
    printf("le livre du numéro\033[31m %d \033[0mn'est pas la bibliothèque\n", n);
    return NULL;
}

LivreH *recherche_titreH(BiblioH *b, char *t){
    /* Recherche un livre dans la bibliothèque par son titre. 
     * La recherche est effectuée en parcourant toutes les listes chaînées de la table de hachage. */
    if (!b)
        return NULL;

    LivreH *l;

    for (int i = 0; i < b->m; i++){                                                          
        l = b->T[i];
        while (l){
            if (strcmp(l->titre, t) == 0){
                printf("le livre est dans la case [%d]\n", i);
                return l;
            }
            l = l->suiv;
        }
    }
    printf("le livre de titre\033[31m %s \033[0mn'est pas la bibliothèque\n", t);
    return NULL;
}


BiblioH *recherche_auteurH(BiblioH *b, char *a){
    
/* Recherche tous les livres d'un auteur dans la bibliothèque. 
 * La recherche est effectuée en parcourant la liste chaînée à la position calculée par la fonction de hachage 
 * à partir du nom de l'auteur. */
    if (!b)
        return NULL;

    BiblioH *b_auteur = creer_biblioH(b->m);
    int pos = fonctionHachage(fonctionClef(a), b->m);
    LivreH *l = b->T[pos];

    while (l){
        if (strcmp(l->auteur, a) == 0){
            inserer(b_auteur, l->num, l->titre, l->auteur);
        }
        l = l->suiv;
    }

    if (b_auteur->nE != 0)
        return b_auteur;

    printf("l'auteur\033[31m %s \033[0mn'a aucun livre dans cette bibliothèque\n", a);
    liberer_biblioH(b_auteur);
    return NULL;

}

void supprimer_ouvrageH(BiblioH *b, int n, char *a, char *t){
    /* Supprime un ouvrage de la bibliothèque en utilisant son numéro, son auteur et son titre. 
     * La fonction utilise la fonction de hachage pour trouver la position de l'ouvrage dans la table de hachage. */
    if (!b)
        return;
    int pos = fonctionHachage(fonctionClef(a), b->m);
    LivreH *l = b->T[pos];
    LivreH *prec = NULL;

    while(l && (l->num != n || strcmp(l->auteur, a) != 0 || strcmp(l->titre, t) != 0)){
        prec = l;
        l = l->suiv;                                                                         
    }
    if(!l){
        printf("le livre n'est pas dans la bibliothèque la suppression est annulée\n");
        return;
    }
    if(!prec){
        b->T[pos] = l->suiv;
        b->nE--;
        liberer_livreH(l);
        return;
    }
    prec->suiv = l->suiv;
    b->nE--;
    liberer_livreH(l);

}

void fusion_bibH(BiblioH *b1, BiblioH *b2){
    /* Fusionne deux bibliothèques en insérant tous les livres de la deuxième bibliothèque dans la première. 
     * Après la fusion, la deuxième bibliothèque est libérée. */

    if (!b1 || !b2)
        return;

    LivreH *l;

    for (int i = 0; i < b2->m; i++){                                                          
        l = b2->T[i];
        while (l){
            inserer(b1, l->num, l->titre, l->auteur);
            l = l->suiv;
        }
    }
    liberer_biblioH(b2);
}

BiblioH *ouvrages_plusieurs_exemplairesH(BiblioH *b){
    /* Crée une nouvelle bibliothèque contenant uniquement les ouvrages qui ont plusieurs exemplaires dans la bibliothèque originale. 
     * La fonction parcourt tous les livres de la bibliothèque originale et insère les livres avec des doublons dans la nouvelle bibliothèque. */
    BiblioH *b_rep = creer_biblioH(b->m);
    LivreH *l1, *l2;
    for (int i = 0; i < b->m; i++){                                                          
        l1 = b->T[i];
        while (l1){
            l2 = l1->suiv;
            while(l2){
                if(strcmp(l1->auteur, l2->auteur) == 0 && strcmp(l1->titre, l2->titre) == 0){
                    inserer(b_rep, l1->num, l1->titre, l1->auteur);
                    inserer(b_rep, l2->num, l2->titre, l2->auteur);
                    break;
                }
                l2 = l2->suiv;
            }
            l1 = l1->suiv;
        }
    }
    if (b_rep->nE != 0)
        return b_rep;
    liberer_biblioH(b_rep);                                                                   
    return NULL;

}
