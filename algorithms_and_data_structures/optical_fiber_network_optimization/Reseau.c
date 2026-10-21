#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>

#include "Reseau.h"
#include "SVGwriter.h"


Reseau *allouerRes(int gamma){
	Reseau *R = (Reseau*)(malloc(sizeof(Reseau)));
    assert(R);
	R->nbNoeuds = 0;
	R->gamma = gamma;
	R->noeuds = NULL;
	R->commodites = NULL;

    return R;

}

void libererReseau(Reseau *R){
    /*Prendre un réseau 
     * libérer sa mémoire allouée*/
    CellNoeud *tempNoeud, *currNoeud = R->noeuds;
    while (currNoeud){
        CellNoeud *tempVoisin, *currVoisin = currNoeud->nd->voisins;
        while (currVoisin){ // Libérer la liste des voisins du noeud
            tempVoisin = currVoisin;
            currVoisin = currVoisin->suiv;
            free(tempVoisin);
        }
        free(currNoeud->nd); // Libérer le noeud
        // Libérer le CellNoeud
        tempNoeud = currNoeud;
        currNoeud = currNoeud->suiv;
        free(tempNoeud);
    }

    CellCommodite *tempCommod, *currCommod = R->commodites;
    while (currCommod) { //Libérer les commodites
        tempCommod = currCommod;
        currCommod = currCommod->suiv;
        free(tempCommod);
    }

    free(R);
}




// 2.1
Noeud* rechercheCreeNoeudListe(Reseau *R, double x, double y){
    /*prendre une réseau et des coordonnées x y 
     * rechercher un nœud avec ces coordonnées 
     * s'il est trouvé, renvoyer le nœud 
     * sinon créer un nouveau nœud avec les mêmes coordonnées l'ajouter au réseau 
     * le renvoyer*/
	
	CellNoeud * current = R->noeuds;
	Noeud * nd;

	while(current){ // la recherche du nœud
		
		nd = current->nd;
		
		if((nd->x == x) && (nd->y == y)){
			return nd;
        //
		}
	
		current = current->suiv;
	}
	
    // s'il n'est pas trouvé
	Noeud * new_nd = (Noeud*)(malloc(sizeof(Noeud)));
	new_nd->x = x;
	new_nd->y = y;
	new_nd->num = R->nbNoeuds + 1;
	new_nd->voisins = NULL;
	
	CellNoeud * new_cell_nd = (CellNoeud*)(malloc(sizeof(CellNoeud)));
	new_cell_nd->nd = new_nd;
    new_cell_nd->suiv = R->noeuds;

    R->noeuds = new_cell_nd;
	R->nbNoeuds = R->nbNoeuds + 1;
	
	return new_nd;
	
}




void ajouterVoisin(Noeud *n1, Noeud *n2){
	
	if((n1->x == n2->x) && (n1->y == n2->y)) return; //On vérifie que les deux mêmes points ne sont pas passé en paramètre
	
    CellNoeud *curr = n1->voisins;
    // vérifier si le 2ème nœud existe déja dans la liste des voisins du premier nœud
    while(curr){
        if(curr->nd == n2)
            return;
        curr = curr->suiv;
    }
    
    //si pas trouvé l'insérer
    CellNoeud *newCell = (CellNoeud *)malloc(sizeof(CellNoeud));
    newCell->nd = n2;
    newCell->suiv = n1->voisins;
    n1->voisins = newCell;
    
    
    CellNoeud *curr2 = n2->voisins;
    // vérifier si le premier nœud existe déja dans la liste des voisins du deuxième nœud
    while(curr2){
        if(curr2->nd == n1)
            return;
        curr2 = curr2->suiv;
    }
    
    //si pas trouvé l'insérer
    CellNoeud *newCell2 = (CellNoeud *)malloc(sizeof(CellNoeud));
    newCell2->nd = n1;
    newCell2->suiv = n2->voisins;
    n2->voisins = newCell2; //Insérage en tête
    
}

void ajouterCommod(CellCommodite **commod, Noeud *extrA, Noeud *extrB){
    /*prendre une chaîne de commodite et deux noeuds
     * créer une commodité entre eux 
     * l'insérer dans la chaîne*/
    CellCommodite * newCom = (CellCommodite*)(malloc(sizeof(CellCommodite)));
    newCom->extrA = extrA;
    newCom->extrB = extrB;

    newCom->suiv = *commod;
    *commod = newCom;

}


// 2.2
Reseau *reconstitueReseauListe(Chaines *C){
    /*Prendre une liste de chaînes 
     * construire un réseau à partir de celle-ci 
     * renvoyer le réseau*/

    assert(C);
	
	Reseau *R = allouerRes(C->gamma);

	CellChaine *currentChaine = C->chaines;
	CellPoint *currentPoint;
	
	Noeud *A, *B, *extA;
	
	while(currentChaine){ // parcourir la liste des chaînes
		currentPoint = currentChaine->points;
		extA = rechercheCreeNoeudListe(R, currentPoint->x, currentPoint->y);
		while(currentPoint){ // parcourir les points
		    A = rechercheCreeNoeudListe(R, currentPoint->x, currentPoint->y);

            if(!currentPoint->suiv){
			    B = rechercheCreeNoeudListe(R, currentPoint->x, currentPoint->y);
			    currentPoint = currentPoint->suiv;
                continue;
            }

			B = rechercheCreeNoeudListe(R, currentPoint->suiv->x, currentPoint->suiv->y);
            ajouterVoisin(A, B);
            
			currentPoint = currentPoint->suiv;
		}
		
        ajouterCommod(&(R->commodites), extA, B);

		currentChaine = currentChaine->suiv;
	}
	
	return R;
}

// 3.1
int nbCommodites(Reseau *R){
    /*Prendre un réseau et renvoyer son nombre de commodites */
    int c = 0;
    CellCommodite *current = R->commodites;
    while(current){
        c++;
        current = current->suiv;
    }
    return c;
}

// 3.1
int nbLiaisons(Reseau *R){
    /*Prendre un réseau et renvoyer son nombre de liaisons */
    int c = 0;
    CellNoeud *N = R->noeuds;
    while(N){
        CellNoeud *current = N->nd->voisins;
        while(current){
            c++;
            current = current->suiv;
        }
        N = N->suiv;
    }
    return c / 2;
}

// 3.2
void ecrireReseau(Reseau *R, FILE *f){
    /*Prendre un réseau et un fichier 
     * écrire le réseau dans le fichier 
     * en respectant le format dans l'enoncé*/
    assert(f);

    fprintf(f, "NbNoeuds : %d\n", R->nbNoeuds);
    fprintf(f, "NbLiaisons : %d\n", nbLiaisons(R));
    fprintf(f, "NbCommodites : %d\n", nbCommodites(R));
    fprintf(f, "Gamma : %d\n", R->gamma);

    fprintf(f, "\n");
    CellNoeud *currentNo = R->noeuds;
    while(currentNo){
        fprintf(f, "v %d %lf %lf \n", currentNo->nd->num, currentNo->nd->x, currentNo->nd->y);
        currentNo = currentNo->suiv;
    }

    fprintf(f, "\n");
    currentNo = R->noeuds;
    while(currentNo){
        CellNoeud *currentNO2 = currentNo->nd->voisins;
        while(currentNO2){
            if(currentNO2->nd->num < currentNo->nd->num)
                fprintf(f, "l %d %d\n", currentNo->nd->num, currentNO2->nd->num);
            currentNO2 = currentNO2->suiv;
        }
        currentNo = currentNo->suiv;
    }

    fprintf(f, "\n");
    CellCommodite *currentCom = R->commodites;
    while(currentCom){
        fprintf(f, "K %d %d\n", currentCom->extrA->num, currentCom->extrB->num);
        currentCom = currentCom->suiv;
    }

}

// code fourni
void afficheReseauSVG(Reseau *R, char* nomInstance){
    CellNoeud *courN,*courv;
    SVGwriter svg;
    double maxx=0,maxy=0,minx=1e6,miny=1e6;

    courN=R->noeuds;
    while (courN!=NULL){
        if (maxx<courN->nd->x) maxx=courN->nd->x;
        if (maxy<courN->nd->y) maxy=courN->nd->y;
        if (minx>courN->nd->x) minx=courN->nd->x;
        if (miny>courN->nd->y) miny=courN->nd->y;
        courN=courN->suiv;
    }
    SVGinit(&svg,nomInstance,500,500);
    courN=R->noeuds;
    while (courN!=NULL){
        SVGpoint(&svg,500*(courN->nd->x-minx)/(maxx-minx),500*(courN->nd->y-miny)/(maxy-miny));
        courv=courN->nd->voisins;
        while (courv!=NULL){
            if (courv->nd->num<courN->nd->num)
                SVGline(&svg,500*(courv->nd->x-minx)/(maxx-minx),500*(courv->nd->y-miny)/(maxy-miny),500*(courN->nd->x-minx)/(maxx-minx),500*(courN->nd->y-miny)/(maxy-miny));
            courv=courv->suiv;
        }
        courN=courN->suiv;
    }
    SVGfinalize(&svg);
}


