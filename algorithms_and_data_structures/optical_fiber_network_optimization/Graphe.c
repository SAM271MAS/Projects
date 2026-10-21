#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "Graphe.h"
#include "Reseau.h"
#include "Struct_File.h"

void printGraphe(Graphe *G){
    /*prendre un graphe et afficher le
     * nous l'avons utilisé pour vérifier si les autres fonctions fonctionnent correctement*/
    printf("nb somm : %d\n", G->nbsom);
    printf("nb commod : %d\n", G->nbcommod);

    for(int i = 0; i < G->nbsom+1; i++){
        if(G->T_som[i] == NULL)
            continue;
        Sommet *s = G->T_som[i];
        printf("Som %d (x: %.2f, y: %.2f):\n", s->num, s->x, s->y);
        Cellule_arete *ca = s->L_voisin;
        while(ca){
            printf(" adj à %d\n", ca->a->v == s->num ? ca->a->u : ca->a->v);
            ca = ca->suiv;
        }
    }

    printf("Commod:\n");
    for(int i = 0; i < G->nbcommod; i++){
        printf("  C %d: de %d à %d\n", i, G->T_commod[i].e1, G->T_commod[i].e2);
    }
}

Graphe *creerGraphe(Reseau *r){
    /*prendre un réseau et créer un graphe à partir de celui-ci*/

    Graphe *G = (Graphe *)(malloc(sizeof(Graphe)));
    G->nbsom = r->nbNoeuds;
    G->nbcommod = nbCommodites(r);
    G->gamma = r->gamma;
    G->T_som = (Sommet **)malloc(sizeof(Sommet)*((G->nbsom )+ 1)); // +1 car les nœuds num commence à 1
    for(int i = 0; i <= G->nbsom; i++){
        G->T_som[i] = NULL;
    }
    G->T_commod = (Commod *)(malloc(sizeof(Commod) * G->nbcommod));

    CellNoeud *currentNd = r->noeuds;
    while(currentNd){
        Sommet *s = (Sommet *)(malloc(sizeof(Sommet)));
        s->num = currentNd->nd->num;
        s->x = currentNd->nd->x;
        s->y = currentNd->nd->y;
        s->L_voisin = NULL;

        CellNoeud *currentNdVois = currentNd->nd->voisins;
        while(currentNdVois){
            // Vérifier si l'arete existe déjà dans la liste des voisins
            Cellule_arete *ca = s->L_voisin;
            while(ca){
                if((ca->a->u == currentNd->nd->num && ca->a->v == currentNdVois->nd->num) || 
                   (ca->a->v == currentNd->nd->num && ca->a->u == currentNdVois->nd->num)){
                    break;
                }
                ca = ca->suiv;
            }
            // s'il n'existe pas créer un nouveau
            if(!ca){
                ca = (Cellule_arete *)(malloc(sizeof(Cellule_arete)));
                Arete *a = (Arete *)(malloc(sizeof(Arete)));
                a->u = currentNd->nd->num;
                a->v = currentNdVois->nd->num;
                ca->a = a;
                ca->suiv = s->L_voisin;
                s->L_voisin = ca;
            }

            currentNdVois = currentNdVois->suiv;
        }
        G->T_som[(s->num)] = s;
        currentNd = currentNd->suiv;
    }
    CellCommodite *currentCom = r->commodites;
    int numcomd = 0;
    while(currentCom){
        Commod com;
        com.e1 = currentCom->extrA->num;
        com.e2= currentCom->extrB->num;
        G->T_commod[numcomd] = com;
        numcomd++;
        currentCom=currentCom->suiv;

    }

    return G;
}


void libererGraphe(Graphe *G) {
    /*prendre un graphe 
     * libérer sa mémoire allouée */
    if(!G)
        return;
    if(G->T_som != NULL) {
        for(int i = 0; i <= G->nbsom; i++){
            if(G->T_som[i] != NULL) {
                Cellule_arete *current = G->T_som[i]->L_voisin;
                while(current != NULL) {
                    Cellule_arete *temp = current;
                    current = current->suiv;
                    if(temp->a)
                        free(temp->a);
                    free(temp);
                }
                free(G->T_som[i]);
            }
        }
        free(G->T_som);
    }
    if(G->T_commod != NULL) {
        free(G->T_commod);
    }
    free(G);
}





int* BFS(Graphe *G, int u, int v, int *nb_aretes) {
    /*prendre un graphe, deux sommets représentant les extrémités d’une chaîne et un pointeur vers un entier
     * utiliser  l'algorithme de parcours en largeur pour trouver le chemin le plus court entre ces deux sommets. 
     * Le pointeur vers *nb_aretes est modifié pour correspondre au nombre minimal d’arêtes dans cette chaîne. 
     *  renvoyer une liste d’entiers, qui représente les sommets visités lors du parcours de cette chaîne*/

    int *visited = (int *)malloc((G->nbsom+1) * sizeof(int));
    int *distance = (int *)malloc((G->nbsom+1) * sizeof(int));
    int *predecessor = (int *)malloc((G->nbsom+1) * sizeof(int));

    for(int i = 0; i <= G->nbsom; i++) {
        visited[i] = 0;
        distance[i] = -1;
        predecessor[i] = -1;
    }

    S_file *F = (S_file *)(malloc(sizeof(S_file)));
    Init_file(F);

    visited[v] = 1;
    distance[v] = 0;
    enfile(F, v);

    while(!estFileVide(F)) {
        int currSom = defile(F);

        if(currSom == u) { // Si le sommet actuel est le sommet cible
            *nb_aretes = distance[u];
            // Create an array to store the chaine
            int* chaine = (int*) malloc((distance[u] + 1) * sizeof(int));
            int chaineInd = distance[u];
            int chaineSom = u;
            while(chaineSom != -1) { // Remplissage de la chaîne avec les sommets visités
                chaine[chaineInd--] = chaineSom;
                chaineSom = predecessor[chaineSom];
            }
            free(F);
            free(visited);
            free(distance);
            free(predecessor);
            return chaine;
        }

        Cellule_arete *ca = G->T_som[currSom]->L_voisin;
        while(ca) {
            int voisSom = ca->a->v == G->T_som[currSom]->num ? ca->a->u : ca->a->v;
            if(ca->a->u == currSom && ca->a->v == voisSom && !visited[voisSom]) {
                enfile(F, voisSom);
                visited[voisSom] = 1;
                distance[voisSom] = distance[currSom] + 1;
                predecessor[voisSom] = currSom;
            }
            ca = ca->suiv;
        }
    }    
    // Si le parcours en largeur est terminé sans avoir visité u
    free(F);
    free(visited);
    free(distance);
    free(predecessor);
    *nb_aretes = -1;
    return NULL;
}



int reorganiseReseau(Reseau* r){
    /*Prendre un réseau 
     * créer le graphe correspondant au réseau
     * retourne 1 si pour toute arête du graphe, 
     * le nombre de chaı̂nes qui passe par cette arête est inférieur à gamma
     * retourne 0 sinon*/

    Graphe *G = creerGraphe(r);
    int *tab[G->nbcommod];
    int tab_size[G->nbcommod];

    Arete *aretes = malloc(G->nbcommod * (G->nbcommod - 1) * sizeof(Arete));
    int *counts = calloc(G->nbcommod * (G->nbcommod - 1), sizeof(int));

    int arete_count = 0; // Compteur pour le nombre d'arêtes
    for(int i = 0; i < G->nbcommod; i++){
        tab[i] = BFS(G, G->T_commod[i].e1, G->T_commod[i].e2, &tab_size[i]);
        for(int j = 0; j < tab_size[i] - 1; j++){
            int boolFound = 0;
            for(int k = 0; k < arete_count; k++){ // Vérifier si l'arête est déjà présente dans le tableau des arêtes
                if((aretes[k].u == tab[i][j] && aretes[k].v == tab[i][j+1]) || (aretes[k].v == tab[i][j] && aretes[k].u == tab[i][j+1])){
                    counts[k]++; // Si oui, incrémenter le compte correspondant
                    if(counts[k] >= r->gamma){ // Si le compte dépasse gamma, libérer la mémoire et retourner 0
                        free(aretes);
                        free(counts);
                        return 0;
                    }
                    boolFound = 1;
                    break;
                }
            }
            // Si l'arête n'est pas trouvée dans le tableau des arêtes
            if(!boolFound){
                if(r->gamma <= 1){ // Si gamma est inférieur ou égal à 1, libérer la mémoire et retourner 0

                    free(aretes);
                    free(counts);
                    return 0;
                }
                // Sinon, ajouter l'arête au tableau des arêtes et incrémenter le compteur d'arêtes
                aretes[arete_count].u = tab[i][j];
                aretes[arete_count].v = tab[i][j+1];
                counts[arete_count] = 1;
                arete_count++;
            }
        }
        free(tab[i]);
    }
    free(aretes);
    free(counts);
    libererGraphe(G);
    return 1;
}
