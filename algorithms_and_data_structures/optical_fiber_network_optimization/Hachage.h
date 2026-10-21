#ifndef __HACHAGE_H__
#define __HACHAGE_H__
#include "Reseau.h"

typedef struct{
  int nbElement;
  int tailleMax;
  CellNoeud** T;
} TableHachage ;

TableHachage *creerTabHash(int M);
void libererTabHash(TableHachage *TabH);
double clef_hachage(double x, double y);
int func_hash(int M, double cle);
Noeud* rechercheCreeNoeudHachage(Reseau* R, TableHachage*H, double x, double y);
Reseau* reconstitueReseauHachage(Chaines *C, int M);

#endif
