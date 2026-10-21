#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

#include "Chaine.h"
#include "Reseau.h"
#include "ArbreQuat.h"


// Fonction pour imprimer un noeud
void printNoeud(Noeud* n){
    if(n != NULL) {
        printf("Noeud num: %d, x: %.2f, y: %.2f\n", n->num, n->x, n->y);
    }
}

// Fonction pour imprimer un arbre quaternaire
void printArbreQuat(ArbreQuat* a){
    if(a != NULL) {
        printf("ArbreQuat xc: %.2f, yc: %.2f, coteX: %.2f, coteY: %.2f\n", a->xc, a->yc, a->coteX, a->coteY);
        printNoeud(a->noeud);
        printf("so\n");
        printArbreQuat(a->so);
        printf("se\n");
        printArbreQuat(a->se);
        printf("no\n");
        printArbreQuat(a->no);
        printf("ne\n");
        printArbreQuat(a->ne);
    }
}


// 5.1
void chaineCoordMinMax(Chaines* C, double* xmin, double* ymin, double* xmax, double* ymax){
    /*détermine les coordonnées minimales et maximales des points constituant les différentes chaı̂nes du réseau*/
	
	CellChaine* liste_chaine = C->chaines;
	CellPoint* current_point;
	
	while(liste_chaine){
		current_point = liste_chaine->points; //POINT DE DEPART
		
		while(current_point){
			
			if(current_point->x > *xmax){
				*xmax = current_point->x;
			}
			if(current_point->x < *xmin){
				*xmin = current_point->x;
			}
			if(current_point->y > *ymax){
				*ymax = current_point->y;
			}
			if(current_point->y < *ymin){
				*ymin = current_point->y;
			}
			
			current_point = current_point->suiv;
		}
		liste_chaine = liste_chaine->suiv;
	}
	
}


ArbreQuat* creerArbreQuat(double xc, double yc, double coteX, double coteY){
    /*Créer un arbre avec les valeurs dans les paramètres
     * et le renvoyer*/

	
	ArbreQuat* abr = (ArbreQuat*)(malloc(sizeof(ArbreQuat)));
	
	abr->xc = xc;
	abr->yc = yc;
	
	abr->coteX = coteX;
	abr->coteY = coteY;
	
	abr->noeud = NULL;
	
	abr->so = NULL;
	abr->se = NULL;
	abr->no = NULL;
	abr->ne = NULL;
	
	return abr;
}

void insererNoeudArbre(Noeud* n, ArbreQuat** a, ArbreQuat* parent){
    /* 
    * insèrer un noeud dans un arbre quaternaire en fonction de ses coordonnées
    */

    if(!*a){ // arbre vide
        int boolOuest = n->x < parent->xc;
        int boolSud = n->y < parent->yc;

        double demicoteX = parent->coteX / 2;
        double demicoteY = parent->coteY / 2;

        double xc = boolOuest ? parent->xc - demicoteX / 2 : parent->xc + demicoteX / 2;
        double yc = boolSud ? parent->yc - demicoteY / 2 : parent->yc + demicoteY / 2;
        ArbreQuat *arbre = creerArbreQuat(xc, yc, demicoteX, demicoteY);

        if(boolSud && boolOuest)
            parent->so = arbre;
        else if(!boolSud && boolOuest)
            parent->no = arbre;
        else if(!boolOuest && boolSud)
            parent->se = arbre;
        else
            parent->ne = arbre;

        arbre->noeud = n;
        *a = arbre;
    }
    else{
        if ((*a)->noeud == NULL){ // feuille
            Noeud *old_n = (*a)->noeud;
            (*a)->noeud = NULL;
            insererNoeudArbre(old_n, a, parent);
            insererNoeudArbre(n, a, parent);
        }
        else if(*a && (*a)->noeud == NULL){ //cellule interne
            int boolOuest = n->x < (*a)->xc;
            int boolSud = n->y < (*a)->yc;

            if(boolSud && boolOuest)
                insererNoeudArbre(n, &((*a)->so), *a);
            else if(!boolSud && boolOuest)
                insererNoeudArbre(n, &((*a)->no), *a);
            else if(!boolOuest && boolSud)
                insererNoeudArbre(n, &((*a)->se), *a);
            else
                insererNoeudArbre(n, &((*a)->ne), *a);
        }
    }
}

void libererArbreQuat(ArbreQuat* a){
    /*Libérer la mémoire allouée à l'arbre*/
    if (a == NULL) {
        return;
    }

    libererArbreQuat(a->so);
    libererArbreQuat(a->se);
    libererArbreQuat(a->no);
    libererArbreQuat(a->ne);

    free(a);
}

Noeud* rechercheCreeNoeudArbre(Reseau* R, ArbreQuat** a, ArbreQuat* parent, double x, double y){
    /*prendre une réseau et des coordonnées x y 
     * rechercher un nœud avec ces coordonnées 
     * s'il est trouvé, renvoyer le nœud 
     * sinon créer un nouveau nœud avec les mêmes coordonnées l'ajouter au réseau 
     * le renvoyer*/

    if (*a == NULL) { // si arbre vide
        Noeud* new_nd = (Noeud*)malloc(sizeof(Noeud));
        R->nbNoeuds++;
        new_nd->num = R->nbNoeuds;
        new_nd->x = x;
        new_nd->y = y;
        new_nd->voisins = NULL;

        CellNoeud* Cn = (CellNoeud*)malloc(sizeof(CellNoeud));
        Cn->nd = new_nd;
        Cn->suiv = R->noeuds;

        R->noeuds = Cn;

        insererNoeudArbre(new_nd, a, parent);

        return new_nd;
    } else if ((*a)->noeud != NULL && (*a)->noeud->x == x && (*a)->noeud->y == y) { // noeud trouvé
        return (*a)->noeud;
    } else {  // continuer la recherche
        int boolOuest = x < (*a)->xc;
        int boolSud = y < (*a)->yc;

        if (boolSud && boolOuest)
            return rechercheCreeNoeudArbre(R, &((*a)->so), *a, x, y);
        if (boolSud && !boolOuest)
            return rechercheCreeNoeudArbre(R, &((*a)->se), *a, x, y);
        if (!boolSud && boolOuest)
            return rechercheCreeNoeudArbre(R, &((*a)->no), *a, x, y);
        if (!boolSud && !boolOuest)
            return rechercheCreeNoeudArbre(R, &((*a)->ne), *a, x, y);
    }

    return NULL;
}




Reseau* reconstitueReseauArbre(Chaines* C){
    /*Prendre une liste de chaînes 
     * construire un réseau à partir de celle-ci 
     * renvoyer le réseau*/
	
	
	Reseau *R = allouerRes(C->gamma);
	
    double xmin = C->chaines->points->x;
	double ymin = C->chaines->points->y;
	double xmax = C->chaines->points->x;
	double ymax = C->chaines->points->y;
	
	chaineCoordMinMax(C, &xmin, &ymin, &xmax, &ymax);
	ArbreQuat *a = creerArbreQuat((xmax-xmin) / 2, (ymax-ymin) / 2, xmax-xmin, ymax-ymin);

	CellChaine *currentChaine = C->chaines;
	CellPoint *currentPoint;
	
    Noeud *A, *B, *extA;
	while(currentChaine){
		currentPoint = currentChaine->points;
        extA = rechercheCreeNoeudArbre(R, &a, NULL, currentPoint->x, currentPoint->y);
		while(currentPoint){
            A = rechercheCreeNoeudArbre(R,  &a, NULL, currentPoint->x, currentPoint->y);

            if(!currentPoint->suiv){
                B = rechercheCreeNoeudArbre(R, &a, NULL, currentPoint->x, currentPoint->y);
                currentPoint = currentPoint->suiv;
                continue;
            }
			B = rechercheCreeNoeudArbre(R, &a, NULL, currentPoint->suiv->x, currentPoint->suiv->y);
            ajouterVoisin(A, B);

			currentPoint = currentPoint->suiv;
		}
        ajouterCommod(&(R->commodites), extA, B);
		currentChaine = currentChaine->suiv;
	}
    // printArbreQuat(a);
    libererArbreQuat(a);
	
    return R;
}



