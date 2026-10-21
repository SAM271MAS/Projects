typedef struct livreh{
    int clef;
    int num;
    char *titre;
    char *auteur;
    struct livreh *suiv;
}LivreH;

typedef struct table {
    int nE ; /*nombre d’elements contenus dans la table de hachage */
    int m ; /*taille de la table de hachage */
    LivreH ** T ; /*table de hachage avec resolution des collisions par chainage */
}BiblioH ;

int fonctionClef(char* auteur);
LivreH* creer_livreH(int num,char* titre,char* auteur);
void liberer_livreH(LivreH* lh);
BiblioH* creer_biblioH(int m);
void liberer_biblioH(BiblioH* bh);
int fonctionHachage(int cle, int m);
void inserer(BiblioH* b,int num,char* titre,char* auteur);
void afficher_livreH(LivreH *l);
void afficher_bibH(BiblioH *b);
LivreH *recherche_numH(BiblioH *b, int n);
LivreH *recherche_titreH(BiblioH *b, char *t);
BiblioH *recherche_auteurH(BiblioH *b, char *a);
void supprimer_ouvrageH(BiblioH *b, int n, char *a, char *t);
void fusion_bibH(BiblioH *b1, BiblioH *b2);
BiblioH *ouvrages_plusieurs_exemplairesH(BiblioH *b);
