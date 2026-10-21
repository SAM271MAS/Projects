
typedef struct livre {
    int num;
    char * titre;
    char * auteur;
    struct livre * suiv;
}Livre ;

typedef struct { /* Tete fictive */
    Livre * L; /* Premier element */
    int num_livre;
}Biblio;

Livre* creer_livre(int num,char* titre,char* auteur);
void liberer_livre(Livre* l);
Biblio* creer_biblio();
void liberer_biblio(Biblio* b);
void inserer_en_tete(Biblio* b,int num,char* titre,char* auteur);
void afficher_livre(Livre *l);
void afficher_bib(Biblio *b);
Livre * recherche_num(Biblio *b, int num);
Livre * recherche_titre(Biblio *b, char *t);
Biblio *recherche_auteur(Biblio *b, char *a);
void supprimer_ouvrage(Biblio *b, int n, char *a, char *t);
void fusion_bib(Biblio *b1, Biblio *b2);
Biblio *ouvrages_plusieurs_exemplaires(Biblio *b);
