#include <stdio.h>
#include <time.h>
#include "entreeSortieLC.h"
#include "entreeSortieH.h"
#include "temp_ccl_rech.h"

clock_t temps_initial;
clock_t temps_final;
double temps_cpu;


// Ce fichier contient des fonctions de test qui servent à répondre aux questions de l'exercice 3.



void ccl_rech_num(Biblio *b, BiblioH *bh, FILE *file){
    /* Effectue et mesure le temps de recherche par numéro dans les deux structure de données.
     * effectue trois types de recherches : 
     * 1. Cas où les livres sont présents.
     * 2. Cas où les livres sont absents.
     * 3. Cas où certains livres sont présents et d'autres absents.
     * Les résultats sont ensuite écrits dans le fichier file.*/



    int nums[SIZE] = {113, 456, 789, 231, 674, 915, 348, 791, 234, 577, 820, 253, 696, 139, 482, 825, 168, 511, 854, 197};
    int absent_nums[SIZE] = {1134, 1456, 1789, 1231, 1674, 1915, 1348, 1791, 1234, 1577, 1820, 1253, 1696, 1139, 1482, 1825, 1168, 1511, 1854, 1197};
    int rand_nums[SIZE] = {113, 456, 789, 231, 674, 915, 348, 791, 234, 577, 1820, 1253, 1696, 1139, 1482, 1825, 1168, 1511, 1854, 1197};
    int i;
    fprintf(file, "recherche par numéro. Cas 1 : livres présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_num(b, nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_num est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_numH est : %f\n", temps_cpu);

    fprintf(file, "\nrecherche par numéro. Cas 2 : livres absents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_num(b, absent_nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_num est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, absent_nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_numH est : %f\n", temps_cpu);

    fprintf(file, "\nrecherche par numéro. Cas 3 : certains absents certains présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_num(b, rand_nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_num est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, rand_nums[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_numH est : %f\n", temps_cpu);
}

void ccl_rech_titre(Biblio *b, BiblioH *bh, FILE *file){
    /* Effectue et mesure le temps de recherche par titre dans les deux structure de données.
     * effectue trois types de recherches : 
     * 1. Cas où les livres sont présents.
     * 2. Cas où les livres sont absents.
     * 3. Cas où certains livres sont présents et d'autres absents.
     * Les résultats sont ensuite écrits dans le fichier file.*/

    char *titre[SIZE] = {"WLRBBMQBHCDARZOWK", "SCDXRJ", "JYBLD", "KEZXDU", "FWKHOPKMCOQHNWNKUE", 
    "JIVSWMDKQT", "LJPTNSNFWZQFJMA", "SOFS", "WPQCA", "KMLNOZJKPQPXR", "BHHKICQC", "FCGPXIQVKUY", 
    "IOHORDTQKVWC", "BOAGUWNNYQXNZLGDGW", "SADEUGUUMOQCDRUBE", "VMXXRDRYXL", "UKWAGM", "MENMEYATDRMYDI", 
    "FMZHLVIHJOU", "MUOTEHZ"};

    char *absent_titre[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", 
    "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20"};

    char *rand_titre[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10","WLRBBMQBHCDARZOWK", 
    "SCDXRJ", "JYBLD", "KEZXDU", "FWKHOPKMCOQHNWNKUE", "JIVSWMDKQT", "LJPTNSNFWZQFJMA", "SOFS", "WPQCA", "KMLNOZJKPQPXR"};

    int i;
    fprintf(file, "recherche par titre. Cas 1 : livres présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titre(b, titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titre est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titreH(bh, titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titreH est : %f\n", temps_cpu);


    fprintf(file, "\nrecherche par titre. Cas 2 : livres absents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titre(b, absent_titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titre est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titreH(bh, absent_titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titreH est : %f\n", temps_cpu);

    fprintf(file, "\nrecherche par titre. Cas 3 : certains absents certains présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titre(b, rand_titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titre est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_titreH(bh, rand_titre[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_titreH est : %f\n", temps_cpu);
}


void ccl_rech_auteur(Biblio *b, BiblioH *bh, FILE *file){
    /* Effectue et mesure le temps de recherche par auteur dans les deux structure de données.
     * effectue trois types de recherches : 
     * 1. Cas où les auteur sont présents.
     * 2. Cas où les auteur sont absents.
     * 3. Cas où certains auteur sont présents et d'autres absents.
     * Les résultats sont ensuite écrits dans le fichier file passé en paramètres.*/
    char *auteur[] = {
        "dneghbctcbx", "cbg", "pxqiywjobspe", "ddiyobqf", "vdrzkmkwl", 
        "vdeqj", "nie", "pym", "otpu", "igocfufbubi", 
        "hkflpbqsvtdw", "ihbxifo", "weuxvegy", "ipbompufpx", "czmaccgw", 
        "coq", "mwk", "uaheyvohlet", "fynzea", "dypvm"
    };

    char *absent_auteur[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", 
    "s10", "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20"};

    char *rand_auteur[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10",
    "hkflpbqsvtdw", "ihbxifo", "weuxvegy", "ipbompufpx", "czmaccgw", 
    "coq", "mwk", "uaheyvohlet", "fynzea", "dypvm"
    };

    int i;
    fprintf(file, "recherche par auteur. Cas 1 : présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteur(b, auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteur est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteurH(bh, auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteurH est : %f\n", temps_cpu);


    fprintf(file, "\nrecherche par auteur. Cas 2 : absents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteur(b, absent_auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteur est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteurH(bh, absent_auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteurH est : %f\n", temps_cpu);

    fprintf(file, "\nrecherche par auteur. Cas 3 : certains absents certains présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteur(b, rand_auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteur est : %f\n", temps_cpu);

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_auteurH(bh, rand_auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour recherche_auteurH est : %f\n", temps_cpu);
}


void ccl_rech_tabH(BiblioH *bh, FILE *file){
    /*
     * Effectue une recherche dans une table de hachage.
     *
     * Elle définit plusieurs tableaux de nombres, titres et auteurs. Certains de ces éléments sont présents dans la bibliothèque, d'autres non.
     *
     * La fonction effectue trois types de recherches :
     * 1. Recherche des éléments présents dans la bibliothèque.
     * 2. Recherche des éléments absents de la bibliothèque.
     * 3. Recherche d'un mélange d'éléments présents et absents.
     *
     * Le temps CPU utilisé est écrit dans le fichier 'file' passé en paramètres.
     */


    int nums[SIZE] = {113, 456, 789, 231, 674, 915, 348, 791, 234, 577, 820, 253, 696, 139, 482, 825, 168, 511, 854, 197};
    int absent_nums[SIZE] = {1134, 1456, 1789, 1231, 1674, 1915, 1348, 1791, 1234, 1577, 1820, 1253, 1696, 1139, 1482, 1825, 1168, 1511, 1854, 1197};
    int rand_nums[SIZE] = {113, 456, 789, 231, 674, 915, 348, 791, 234, 577, 1820, 1253, 1696, 1139, 1482, 1825, 1168, 1511, 1854, 1197};

    char *titre[SIZE] = {"WLRBBMQBHCDARZOWK", "SCDXRJ", "JYBLD", "KEZXDU", "FWKHOPKMCOQHNWNKUE", 
    "JIVSWMDKQT", "LJPTNSNFWZQFJMA", "SOFS", "WPQCA", "KMLNOZJKPQPXR", "BHHKICQC", "FCGPXIQVKUY", 
    "IOHORDTQKVWC", "BOAGUWNNYQXNZLGDGW", "SADEUGUUMOQCDRUBE", "VMXXRDRYXL", "UKWAGM", "MENMEYATDRMYDI", 
    "FMZHLVIHJOU", "MUOTEHZ"};

    char *absent_titre[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", 
    "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20"};

    char *rand_titre[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10","WLRBBMQBHCDARZOWK", 
    "SCDXRJ", "JYBLD", "KEZXDU", "FWKHOPKMCOQHNWNKUE", "JIVSWMDKQT", "LJPTNSNFWZQFJMA", "SOFS", "WPQCA", "KMLNOZJKPQPXR"};

    char *auteur[] = {
        "dneghbctcbx", "cbg", "pxqiywjobspe", "ddiyobqf", "vdrzkmkwl", 
        "vdeqj", "nie", "pym", "otpu", "igocfufbubi", 
        "hkflpbqsvtdw", "ihbxifo", "weuxvegy", "ipbompufpx", "czmaccgw", 
        "coq", "mwk", "uaheyvohlet", "fynzea", "dypvm"
    };

    char *absent_auteur[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", 
    "s10", "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20"};

    char *rand_auteur[SIZE] = {"s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10",
    "hkflpbqsvtdw", "ihbxifo", "weuxvegy", "ipbompufpx", "czmaccgw", 
    "coq", "mwk", "uaheyvohlet", "fynzea", "dypvm"
    };

    int i;
    fprintf(file, "rechercheH. Cas 1 : présents\n");


    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, nums[i]);
        recherche_titreH(bh, titre[i]);
        recherche_auteurH(bh, auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour rechercheH est : %f\n", temps_cpu);

    fprintf(file, "\nrechercheH. Cas 2 : absents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, absent_nums[i]);
        recherche_titreH(bh, absent_titre[i]);
        recherche_auteurH(bh, absent_auteur[i]);
    }
    temps_final = clock(); 
    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour rechercheH est : %f\n", temps_cpu);

    fprintf(file, "\nrechercheH. Cas 3 : certains absents certains présents\n");

    temps_initial = clock();
    for(i = 0; i < SIZE; i++){
        recherche_numH(bh, rand_nums[i]);
        recherche_titreH(bh, rand_titre[i]);
        recherche_auteurH(bh, rand_auteur[i]);
    }
    temps_final = clock(); 

    temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
    fprintf(file, "le temps qu'il a fallu pour rechercheH est : %f\n", temps_cpu);
}



void ccl_plus_exemp(FILE *file){
    /*
     * Effectue et mesure le temps de recherche d'ouvrages avec plusieurs exemplaires dans les deux structure de données.
     *
     * Pour chaque taille de bibliothèque, elle effectue les opérations suivantes :
     * 4. Calcule le temps CPU utilisé pour la recherche dans les deux bibliothèques et l'écrit dans le fichier 'file' passé en paramètres.
     * 6. Libère la mémoire allouée pour la bibliothèque et la bibliothèque de hachage.
     *
     * Cette fonction permet d'évaluer l'efficacité de la recherche d'ouvrages avec plusieurs exemplaires dans une bibliothèque et une bibliothèque de hachage en fonction de la taille de la bibliothèque.
     */


    for (int i = 1000; i < 20000; i+=1000){
        Biblio *b = charger_n_entrees("GdeBiblio.txt", i);
        BiblioH *bh = charger_n_entreesH("GdeBiblio.txt", i, 1000);
        
        temps_initial = clock();
        ouvrages_plusieurs_exemplaires(b);
        temps_final = clock();       
        
        temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
        fprintf(file, "%d %f", i, temps_cpu);                                                                      
        
        temps_initial = clock();
        ouvrages_plusieurs_exemplairesH(bh);
        temps_final = clock();       
        
        temps_cpu =((double) (temps_final - temps_initial)) / CLOCKS_PER_SEC ;
        fprintf(file, " %f\n",  temps_cpu);
        liberer_biblio(b);
        liberer_biblioH(bh);
    }


}
