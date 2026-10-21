#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <assert.h>

#include "Hachage.h"
#include "Chaine.h"
#include "Reseau.h"

TableHachage *creerTabHash(int M){
    /*Prendre un entier M
     * créer une table de hachage avec M cas initiés à NULL*/
    TableHachage *TabH = (TableHachage *)(malloc(sizeof(TableHachage)));
    assert(TabH);
    TabH->nbElement = 0;

    TabH->tailleMax = M;
    TabH->T = (CellNoeud**) malloc(M * sizeof(CellNoeud*));;
    assert(TabH->T);

    for(int i = 0; i < M; i++){
        TabH->T[i] = NULL;
  }

    return TabH;
}
void libererTabHash(TableHachage *TabH){
    /*Prend une table de hachage et libère la mémoire allouée*/
    if(TabH == NULL) return;

    for(int i = 0; i < TabH->tailleMax; i++){
        CellNoeud *current = TabH->T[i];
        while(current != NULL){
            CellNoeud *temp = current;
            current = current->suiv;
            if(temp != NULL){
                free(temp); //  libérons seulement la cellule, pas le nœud.
                temp = NULL;
            }
        }
    }

    if(TabH->T != NULL){
        free(TabH->T);
        TabH->T = NULL;
    }

    free(TabH);
    TabH = NULL;
}



// 4.2
double clef_hachage(double x, double y){
    /*Prendre deux entiers et renvoie une clé*/
    return (y+(x + y)*(x + y +1)) / 2;
}

// 4.3
int func_hash(int M, double cle){
    /*Prendre la taille d'une table et une clé 
     * renvoie un entier compris entre 0 et la taille M*/
    double A = (sqrt(5) - 1)/2;
    return M * (cle * A - (int)floor(cle * A));
}

// 4.4
Noeud* rechercheCreeNoeudHachage(Reseau* R, TableHachage *H, double x, double y){
    /*prendre une réseau et des coordonnées x y 
     * rechercher un nœud avec ces coordonnées 
     * s'il est trouvé, renvoyer le nœud 
     * sinon créer un nouveau nœud avec les mêmes coordonnées l'ajouter au réseau 
     * le renvoyer*/

    //calculer l'indice
    int cle = clef_hachage(x, y);
    int indiceH = func_hash(H->tailleMax,  cle);

    Noeud *nd;
    CellNoeud *current = H->T[indiceH];

    while(current){ // recherche dans le case
        nd = current->nd;

        if((nd->x == x) && (nd->y ==y)){
            return nd;
        }

        current = current->suiv;
    }

    // si pas trouvé
    Noeud *new_nd = (Noeud*)(malloc(sizeof(Noeud)));
    new_nd->x = x;
    new_nd->y = y;
    new_nd->num = R->nbNoeuds + 1;
    new_nd->voisins = NULL;
    
    // Insertion table de hachage
    CellNoeud * new_cell_nd_hash = (CellNoeud*)(malloc(sizeof(CellNoeud)));
    new_cell_nd_hash->nd = new_nd;
    new_cell_nd_hash->suiv = H->T[indiceH];
    H->T[indiceH] = new_cell_nd_hash;
    H->nbElement = H->nbElement + 1;

    // Insertion réseau                                                                                                      
    CellNoeud * new_cell_nd_net = (CellNoeud*)(malloc(sizeof(CellNoeud)));
    new_cell_nd_net->nd = new_nd;
    new_cell_nd_net->suiv = R->noeuds;                                                                             
    R->noeuds = new_cell_nd_net;
    R->nbNoeuds = R->nbNoeuds + 1;


    return new_nd;

}
// 4.5
Reseau* reconstitueReseauHachage(Chaines *C, int M){
    /*Prendre une liste de chaînes 
     * construire un réseau à partir de celle-ci 
     * renvoyer le réseau*/
    assert(C);                                                                                          
          
    Reseau *R = allouerRes(C->gamma);

    TableHachage *H = creerTabHash(M);

    CellChaine *currentChaine = C->chaines;
    CellPoint *currentPoint;
    
    Noeud *A, *B, *extA;

    while(currentChaine){
        currentPoint = currentChaine->points;
        extA = rechercheCreeNoeudHachage(R, H, currentPoint->x, currentPoint->y);
        while(currentPoint){
            A = rechercheCreeNoeudHachage(R, H, currentPoint->x, currentPoint->y);

            if(!currentPoint->suiv){
                B = rechercheCreeNoeudHachage(R, H, currentPoint->x, currentPoint->y);
                currentPoint = currentPoint->suiv;
                continue;
            }

            B = rechercheCreeNoeudHachage(R, H, currentPoint->suiv->x, currentPoint->suiv->y);
            ajouterVoisin(A, B);
            
            currentPoint = currentPoint->suiv;
        }

        ajouterCommod(&(R->commodites), extA, B);
            

        currentChaine = currentChaine->suiv;
    }
    libererTabHash(H);

    return R;
}


