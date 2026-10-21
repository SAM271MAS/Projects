#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "entreeSortieLC.h"
#include "entreeSortieH.h"
#include "temp_ccl_rech.h"


void menu(){
    printf("Veuillez choisir une option :\n");
    printf("0 - Sortie du programme\n");
    printf("1 - Affichage\n");
    printf("2 - Insérer un ouvrage\n");
    printf("3 - Rechercher un ouvrage par son numéro\n");
    printf("4 - Rechercher un ouvrage par son titre\n");
    printf("5 - Rechercher les ouvrages d'un auteur\n");
    printf("6 - Supprimer un ouvrage\n");
}

int main(int argc, char** argv){

    if(argc != 3){
        printf("Erreur : utilisation incorrecte. Voici un exemple d'utilisation :\n./main <nom_du_fichier> <nb_ligne>\n");
        return EXIT_FAILURE;
    }

    /*Exercice 1*/

    Biblio *b = charger_n_entrees(argv[1], strtol(argv[2], NULL, 10));
    Biblio *b2 = charger_n_entrees(argv[1], strtol(argv[2], NULL, 10));

    enregistrer_biblio(b, "biblioLC.txt");

    printf("\nrecherche_num:\n");
    afficher_livre(recherche_num(b, 1));
    afficher_livre(recherche_num(b, -1));

    printf("\nrecherche_titre:\n");
    afficher_livre(recherche_titre(b, "JYBLD"));
    afficher_livre(recherche_titre(b, "test"));

    printf("\nrecherche_auteur:\n");
    Biblio *b_r_a = recherche_auteur(b, "adrr");
    afficher_bib(b_r_a);
    liberer_biblio(b_r_a);
    Biblio *b_r_a2 = recherche_auteur(b, "test");
    afficher_bib(b_r_a2);
    liberer_biblio(b_r_a2);

    printf("\nsupprimer_ouvrage:\n");
    supprimer_ouvrage(b,  0, "yhidd", "WLRBBMQBHCDARZOWK");
    supprimer_ouvrage(b,  9, "test", "SOFS");

    printf("fusion_bib:\n");
    fusion_bib(b,b2);
    // b2 est librer dans la fonction fusion_bib
    afficher_bib(b);

    printf("ouvrage_plus_exemp:\n");
    Biblio *b_o_p = ouvrages_plusieurs_exemplaires(b);
    afficher_bib(b_o_p);
    liberer_biblio(b_o_p);


    // laissez commenté si vous voulez utiliser le code de l’ex 1.8
    liberer_biblio(b);



    /*Exercice 1.8*/

    // int rep, num;
    // char buffer[256], titre[256], auteur[256];
    // do{
    //     menu();
    //     fgets(buffer, sizeof(buffer), stdin);
    //     sscanf(buffer, "%d", &rep);
    //     switch (rep){
    //         case 1:
    //             printf("Affichage :\n");
    //             afficher_bib(b);
    //             break;
    //         case 2:
    //             printf("Veuillez entrer le numéro, le titre et l'auteur de l'ouvrage.\n");
    //             fgets(buffer, sizeof(buffer), stdin);
    //             if (sscanf(buffer, "%d %s %s", &num, titre, auteur) == 3) {
    //                 inserer_en_tete(b, num, titre, auteur);
    //                 printf("Ajout fait.\n");
    //             } else{
    //                 printf("\033[31mErreur format\033[0m\n");
    //             }
    //             break;
    //         case 3:
    //             printf("Veuillez entrer le numéro de l’ouvrage cherché\n");
    //             fgets(buffer, sizeof(buffer), stdin);
    //             if (sscanf(buffer, "%d", &num) == 1) {
    //                 afficher_livre(recherche_num(b, num));
    //             } else{
    //                 printf("\033[31mErreur format\033[0m\n");
    //             }
    //             break;
    //         case 4:
    //             printf("Veuillez entrer le titre de l’ouvrage cherché\n");
    //             fgets(buffer, sizeof(buffer), stdin);
    //             if (sscanf(buffer, "%s", titre) == 1) {
    //                 afficher_livre(recherche_titre(b, titre));
    //             } else{
    //                 printf("\033[31mErreur format\033[0m\n");
    //             }
    //             break;
    //         case 5:
    //             printf("Veuillez entrer le nom de de l'auteur\n");
    //             fgets(buffer, sizeof(buffer), stdin);
    //             if (sscanf(buffer, "%s", auteur) == 1) {
    //                 Biblio *b_r_a = recherche_auteur(b, auteur);
    //                 afficher_bib(b_r_a);
    //                 liberer_biblio(b_r_a);
    //             } else{
    //                 printf("\033[31mErreur format\033[0m\n");
    //             }
    //             break;
    //         case 6:
    //             printf("Veuillez entrer le numéro, le titre et l'auteur de l'ouvrage.\n");
    //             fgets(buffer, sizeof(buffer), stdin);
    //             if (sscanf(buffer, "%d %s %s", &num, titre, auteur) == 3) {
    //                 supprimer_ouvrage(b,  num, auteur, titre);
    //                 printf("est supprimé.\n");
    //             } else{
    //                 printf("\033[31mErreur format\033[0m\n");
    //             }
    //             break;
    //     }
    // }while (rep != 0);
    // printf("Merci, et au revoir.\n");
    // liberer_biblio(b);
    // return EXIT_SUCCESS;
    //


    /*Exercice 2*/

    BiblioH *bh = charger_n_entreesH(argv[1], strtol(argv[2], NULL, 10), strtol(argv[2], NULL, 10));
    BiblioH *bh2 = charger_n_entreesH(argv[1], strtol(argv[2], NULL, 10), strtol(argv[2], NULL, 10));

    enregistrer_biblioH(bh, "biblioH.txt");
    afficher_bibH(bh);

    printf("\nrecherche_numH:\n");
    afficher_livreH(recherche_numH(bh, 1));
    afficher_livreH(recherche_numH(bh, -1));
    
    printf("\nrecherche_titreH:\n");
    afficher_livreH(recherche_titreH(bh, "JYBLD"));
    afficher_livreH(recherche_titreH(bh, "test"));
    
    printf("\nrecherche_auteur:\n");
    BiblioH *b_r_aH = recherche_auteurH(bh, "adrr");
    afficher_bibH(b_r_aH);
    liberer_biblioH(b_r_aH);
    BiblioH *b_r_a2H = recherche_auteurH(bh, "test");
    afficher_bibH(b_r_a2H);
    liberer_biblioH(b_r_a2H);
    
    printf("\nsupprimer_ouvrageH:\n");
    supprimer_ouvrageH(bh,  0, "yhidd", "WLRBBMQBHCDARZOWK");
    supprimer_ouvrageH(bh,  8, "test", "SOFS");
    afficher_bibH(bh);



    printf("fusion_bibH:\n");
    fusion_bibH(bh,bh2);
    // bh2 est librer dans la fonction fusion_bib
    afficher_bibH(bh);
    
    printf("ouvrage_plus_exempH:\n");
    BiblioH *b_o_pH = ouvrages_plusieurs_exemplairesH(bh);
    afficher_bibH(b_o_pH);
    liberer_biblioH(b_o_pH);

    liberer_biblioH(bh);


    /*Exercice 3*/
    Biblio *b_ex3 = charger_n_entrees("GdeBiblio.txt", 1000);
    BiblioH *bh_ex3 = charger_n_entreesH("GdeBiblio.txt", 1000, 500);

    FILE *file = fopen("temps_de_calcul_recherche.txt", "w");
    assert(file);

    /*Exercice 3.1*/
    ccl_rech_num(b_ex3, bh_ex3, file);
    fprintf(file, "\n\n");
    ccl_rech_titre(b_ex3, bh_ex3, file);
    fprintf(file, "\n\n");
    ccl_rech_auteur(b_ex3, bh_ex3, file);

    fprintf(file, "\n\nex3.2\n\n");


    /*Exercice 3.2*/
    fprintf(file, "taille 100\n\n");
    BiblioH *bh_ex3_1 = charger_n_entreesH("GdeBiblio.txt", 1000, 100);
    ccl_rech_tabH(bh_ex3_1, file);
    liberer_biblioH(bh_ex3_1);

    fprintf(file, "\n\ntaille 200\n\n");
    BiblioH *bh_ex3_2 = charger_n_entreesH("GdeBiblio.txt", 1000, 100);
    ccl_rech_tabH(bh_ex3_2, file);
    liberer_biblioH(bh_ex3_2);

    fprintf(file, "\n\ntaille 500\n\n");
    ccl_rech_tabH(bh_ex3, file);

    fprintf(file, "\n\ntaille 1000\n\n");
    BiblioH *bh_ex3_3 = charger_n_entreesH("GdeBiblio.txt", 1000, 100);
    ccl_rech_tabH(bh_ex3_3, file);
    liberer_biblioH(bh_ex3_3);

    fclose(file);

    liberer_biblio(b_ex3);
    liberer_biblioH(bh_ex3);

    /*Exercice 3.3*/
    FILE *file2 = fopen("plus_exemp.txt", "w");
    assert(file2);

    ccl_plus_exemp(file2);
    fclose(file2);
    printf("\x1b[2J\x1b[1;1H"); 
    return EXIT_SUCCESS;

}
