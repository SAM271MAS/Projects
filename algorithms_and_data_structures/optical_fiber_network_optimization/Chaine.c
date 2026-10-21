#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "Chaine.h"
#include "SVGwriter.h"                                                                                             


// Fonctions de créations et d'insertions en tête des listes chaînées
CellPoint *creerCellPoint(double x, double y){
    CellPoint *cp = (CellPoint *)malloc(sizeof(CellPoint));
    assert(cp);

    cp->x = x;
    cp->y = y;
    cp->suiv = NULL;

    return cp;
}

CellChaine *creerCellChaine(CellPoint *cp){
    CellChaine *cc = (CellChaine *)malloc(sizeof(CellChaine));
    assert(cc);

    cc->numero = 0;
    cc->points = cp;
    cc->suiv = NULL;

    return cc;
}

Chaines *creerChaines(int gamma, int nbChaines, CellChaine *chaines){
    Chaines *ch = (Chaines *)malloc(sizeof(Chaines));
    assert(ch);
 
    ch->gamma = gamma;
    ch->nbChaines = nbChaines;
    ch->chaines = chaines;
 
    return ch;
}

void libererChaines(Chaines *ch){
    CellChaine *cc = ch->chaines;
    CellChaine *cc_suiv;

    while (cc != NULL){
        cc_suiv = cc->suiv;

        CellPoint *cp = cc->points;
        CellPoint *cp_suiv;

        while (cp != NULL){
            cp_suiv = cp->suiv;
            free(cp);
            cp = cp_suiv;
        }

        free(cc);
        cc = cc_suiv;
    }
    free(ch);
}

void insererPoint(CellPoint **cpl, CellPoint *cp){
    cp->suiv = *cpl;
    *cpl = cp;
}

void insererCellChaine(CellChaine **ccl, CellChaine *cc){
    cc->numero = (*ccl)->numero+1;
    cc->suiv = *ccl;
    *ccl = cc;                                                                                           
}


// 1.1
Chaines *lectureChaines(FILE * f){
    /*Prendre un fichier dont la forme est comme dans l'exemple de l'enoncé 
     * le lire ligne par ligne pour créer une liste de chaı̂nes et la renvoyer*/

    assert(f);

    int nbChaines, gamma, nbPoints;
    double x, y;

    char buffer[256];

    CellPoint *pt = NULL;
    CellChaine *chaine = NULL;
    Chaines *liste_chaines = NULL;

    // lire les deux premières lignes
    fgets(buffer, 256, f);
    sscanf(buffer, "NbChain :%d", &nbChaines);
    fgets(buffer, 256, f);
    sscanf(buffer, "Gamma :%d", &gamma);

    while (fgets(buffer, 256, f) != NULL) {  // parcourir les lignes / chaı̂ne
        sscanf(buffer, "%*d %d %[^\n]", &nbPoints, buffer);

        for (int i = 0; i < nbPoints; i++){  // parcourir les points
            sscanf(buffer, "%lf %lf %[^\n]", &x, &y, buffer);

            CellPoint *new_pt = creerCellPoint(x, y);

            if (i == 0)
                pt = new_pt;
            else
                insererPoint(&pt, new_pt);
            
        }
        CellChaine *new_chaine = creerCellChaine(pt);
        if (!chaine)
            chaine = new_chaine;
        else
            insererCellChaine(&chaine, new_chaine);
    }
    
    liste_chaines = creerChaines(gamma, nbChaines, chaine);                                    
    return liste_chaines;                                                                      
} 
 

int tailleChaine(CellChaine *chaine){
    /*prendre une chaîne 
     * renvoyer ces nombre des points*/

    CellPoint* point = chaine->points;
    int i = 0;
    while(point){
        i++;
        point = point->suiv;
    }
    return i;
}



// 1.2
void ecrireChaines(Chaines *C, FILE *f){
    /*prendre un fichier et une liste de chaînes 
     * écrire le contenu des chaînes dans le fichier 
     * comme le format spécifié en ex 1.1*/
    if(f != NULL){

        fprintf(f,"NbChain: %d\n", C->nbChaines); //NB de Chaînes
        fprintf(f,"Gamma: %d\n", C->gamma); //NB Gamma

        CellChaine *chaineLC = C->chaines;
        CellPoint *pt;

        while(chaineLC){
            fprintf(f, "%d ", chaineLC->numero);
            fprintf(f, "%d ", tailleChaine(chaineLC));

            pt = chaineLC->points;

            while(pt){
                fprintf(f, "%.2f ", pt->x);
                fprintf(f, "%.2f ", pt->y);
                pt = pt->suiv;
            }
            fprintf(f,"\n");
            chaineLC = chaineLC->suiv;
        }
    }
}



// 1.3
void afficheChainesSVG(Chaines *C, char* nomInstance){
    /* code fourni */
    // int i;
    double maxx=0,maxy=0,minx=1e6,miny=1e6;
    CellChaine *ccour;
    CellPoint *pcour;
    double precx,precy;
    SVGwriter svg;
    ccour=C->chaines;
    while (ccour!=NULL){
        pcour=ccour->points;
        while (pcour!=NULL){
            if (maxx<pcour->x) maxx=pcour->x;
            if (maxy<pcour->y) maxy=pcour->y;
            if (minx>pcour->x) minx=pcour->x;
            if (miny>pcour->y) miny=pcour->y;  
            pcour=pcour->suiv;
        }
    ccour=ccour->suiv;
    }
    SVGinit(&svg,nomInstance,500,500);
    ccour=C->chaines;
    while (ccour!=NULL){
        pcour=ccour->points;
        SVGlineRandColor(&svg);
        SVGpoint(&svg,500*(pcour->x-minx)/(maxx-minx),500*(pcour->y-miny)/(maxy-miny)); 
        precx=pcour->x;
        precy=pcour->y;  
        pcour=pcour->suiv;
        while (pcour!=NULL){
            SVGline(&svg,500*(precx-minx)/(maxx-minx),500*(precy-miny)/(maxy-miny),500*(pcour->x-minx)/(maxx-minx),500*(pcour->y-miny)/(maxy-miny));
            SVGpoint(&svg,500*(pcour->x-minx)/(maxx-minx),500*(pcour->y-miny)/(maxy-miny));
            precx=pcour->x;
            precy=pcour->y;    
            pcour=pcour->suiv;
        }
        ccour=ccour->suiv;
    }
    SVGfinalize(&svg);
}

// 1.4
double longueurChaine(CellChaine *c){
    /* prendre une chaı̂ne
     * renvoyer sa longueur physique*/

    CellPoint *p1 = c->points;
    CellPoint *p2;

    double distance = 0;

    while(p1->suiv){ // Calculer la distance entre les points
        p2 = p1->suiv;

        distance += sqrt(pow(p2->x - p1->x, 2) + pow(p2->y - p1->y, 2));

        p1 = p2;
    }
    return distance;

}


// 1.4
double longueurTotale(Chaines *C){
    /* prendre une liste de chaı̂nes
     * renvoyer sa longueur physique totale*/

    double distance = 0;
    CellChaine *chaines = C->chaines;

    for(int i=0; i<C->nbChaines; i++){ // parcourir les chaînes en ajoutant leur longueurs totale
        distance += longueurChaine(chaines);
        chaines = chaines->suiv;
    }
    return distance;
}

// 1.5
int comptePointsTotal(Chaines *C){
    /* prendre une liste de chaı̂nes
     * renvoyer le nombre total d’occurrences de points*/

    int c = 0;
    
    CellChaine *chaine = C->chaines;
    CellPoint *point;
    
    while(chaine){
        point = chaine->points;
        
        while(point){
            c++;
            point=point->suiv;
        }
        chaine = chaine->suiv;
    }
    return c;
}


