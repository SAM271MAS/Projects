#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>
#include "Chaine.h"
#include "Hachage.h"
#include "Reseau.h"
#include "ArbreQuat.h"

clock_t temps_initial;
clock_t temps_final;
double temps_cpu;

//6.1
void ccl_temp_liste(Chaines *C, FILE *f){
    /*prendre un fichier et une liste de chaînes C
     * y écrit le temps qu'il a fallu à la fonction reconstitueReseauListe(C) pour se terminer 
     * le temps est en secondes*/


    temps_initial = clock();
    reconstitueReseauListe(C);
    temps_final = clock();

    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
    fprintf(f, "le temps qu'il a fallu pour reconstitueReseauListe est : %f\n", temps_cpu);
}

//6.1
void ccl_temp_hach(Chaines *C, FILE *f, int M){
    /*prendre un fichier, la taille de la table de hachage et une liste de chaînes C
     * y écrit le temps qu'il a fallu à la fonction reconstitueReseauHachag(C, M) pour se terminer 
     * le temps est en secondes*/

    temps_initial = clock();
    reconstitueReseauHachage(C, M);
    temps_final = clock();

    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
    fprintf(f, "le temps qu'il a fallu pour reconstitueReseauHachage avec %d comme taille est : %f\n",M ,temps_cpu);
}

//6.1
void ccl_temp_arbre(Chaines *C, FILE *f){
    /*prendre un fichier et une liste de chaînes C
     * y écrit le temps qu'il a fallu à la fonction reconstitueReseauArbre(C) pour se terminer 
     * le temps est en secondes*/

    temps_initial = clock();
    reconstitueReseauArbre(C);
    temps_final = clock();

    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
    fprintf(f, "le temps qu'il a fallu pour reconstitueReseauArbre est : %f\n", temps_cpu);
}


//6.2
Chaines *generationAleatoire(int nbChaines,int nbPointsChaine,int xmax, int ymax){
    /*prendre le nombre de chaı̂nes à créer, le nombre de points par chaı̂ne et les coordonnées maximales des points
     *renvoyer une liste de chaînes avec les paramètres spécifiés*/
    double x, y;

    CellPoint *pt = NULL;
    CellChaine *chaine = NULL;
    Chaines *liste_chaines = NULL;

    for (int i = 0; i < nbChaines; i++){
        for (int j = 0; j < nbPointsChaine; j++){
            x = ((float)rand()/(float)(RAND_MAX)) * xmax;
            y = ((float)rand()/(float)(RAND_MAX)) * ymax;
            CellPoint *newPt = creerCellPoint(x,  y);

            if (j == 0)
                pt = newPt;
            else
                insererPoint(&pt,  newPt);
        }
        CellChaine *newChaine = creerCellChaine(pt);
        if(!chaine)
            chaine = newChaine;
        else
            insererCellChaine(&chaine, newChaine);

    }
    liste_chaines = creerChaines(0, nbChaines, chaine);
    return liste_chaines;
}

int main(){

    srand(time(NULL));

    // FILE *fileChaine = fopen("00014_burma.cha", "r");
    // assert(fileChaine);
    //
    // Chaines *chaines = lectureChaines(fileChaine);
    // fclose(fileChaine);
    //
    // // 6.1
    // FILE *fStats = fopen("Stats_ex6_1.txt", "w");
    // assert(fStats);
    //
    // ccl_temp_liste(chaines, fStats);
    // ccl_temp_arbre(chaines, fStats);
    //
    //
    // for(int i= 1000; i <= 10000; i+=1000){ // Modifier la taille de la table de hachage
    //     ccl_temp_hach(chaines, fStats, i);
    // }
    //
    // fclose(fStats);
    
    //6.2 test de la fonction generationAleatoire

    // Chaines *chaines2 = generationAleatoire(10,  5, 100, 80);
    // FILE *f = fopen("test_gener_Alea.cha", "w");
    // assert(f);
    // ecrireChaines(chaines2, f);
    // fclose(f);

    //6.3
    // pour essayer de mesurer le temps il suffit de supprimer les commentaires du code de la structure mesurée

    // liste
    // FILE *plotL = fopen("plotL.txt", "w");
    // assert(plotL);
    
    // table de hachage
    // FILE *plotH = fopen("plotHachage.txt", "w");
    // assert(plotH);
    // int tailleHash = 1000;

    // arbre
    // FILE *plotA = fopen("plotArbre.txt", "w");
    // assert(plotA);


    // Reseau *R;
    
    // for (int i = 500; i <= 5000; i+=500){ // boucle pour varier le nombre de chaı̂nes de 500 à 5000 par pas de 500
    //     Chaines *chaineGraphe = generationAleatoire(i, 100, 5000, 5000);
    //     printf("%d\n", i);

        // liste
        // temps_initial = clock();
        // R = reconstitueReseauListe(chaineGraphe);
        // temps_final = clock();
        // temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
        // fprintf(plotL,"%d %f\n", i, temps_cpu);

        // table de hachage
        // temps_initial = clock();
        // R = reconstitueReseauHachage(chaineGraphe, tailleHash);
        // temps_final = clock();
        // temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
        // fprintf(plotH,"%d %f\n", i, temps_cpu);


        // arbre
        // temps_initial = clock();
        // R = reconstitueReseauArbre(chaineGraphe);
        // temps_final = clock();
        // temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC;
        // fprintf(plotA,"%d %f\n", i, temps_cpu);

    // }
    // libererReseau(R);
    // fclose(plotL);
    // fclose(plotH);
    // fclose(plotA);



    return EXIT_SUCCESS;
}
