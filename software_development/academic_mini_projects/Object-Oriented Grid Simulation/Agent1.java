import java.util.ArrayList;

public class Agent1{
    private int x, y;
    private ArrayList<Joyau> sac = new ArrayList<>();

    private static Agent1 instance;

    //Constructeur
    private Agent1(int x, int y) {
        this.x = x;
        this.y = y;
        sac = new ArrayList<>();
    }

    // Public static method to access the single instance
    public static Agent1 getInstance(int x, int y) {
        if (instance == null) {
            instance = new Agent1(x, y);
        }
        return instance;
    }


    //Accesseurs
    public int getX(){
        return x;
    }
    public int getY(){
        return y;
    }


    //Mutateurs
    public void setX(int x){
        this.x = x;
    }
    public void setY(int y){
        this.y = y;
    }

    public void seDeplacer(Grille t, int xnew, int ynew)throws CoordonneesIncorrectesException, DeplacementIncorrectException, CaseNonPleineException{
        /**
        * Déplace l'agent dans la grille vers de nouvelles coordonnées.
        *
        * @param t La grille.
        * @param xnew La nouvelle coordonnée x.
        * @param ynew La nouvelle coordonnée y.
        * @throws DeplacementIncorrectException Si les nouvelles coordonnées sont hors limites.
        * @throws CoordonneesIncorrectesException de la class Grille.
        * @throws CaseNonPleineException de la class Grille.
        */
        if (xnew < t.nbColonnes && ynew < t.nbLignes){
            x = xnew;
            y = ynew;

            if (t.caseEstVide(xnew, ynew))
                return;

            Contenu contenuCase = t.getCase(xnew, ynew);

            if (contenuCase instanceof Gardien){
                sac.clear();

            }
            else if (contenuCase instanceof Joyau){
                sac.add((Joyau)(t.videCase(xnew, ynew)));
            }
        }

        else{
            if (xnew < t.nbColonnes){
                throw new DeplacementIncorrectException("déplacement impossible x");
            }
            else{
                throw new DeplacementIncorrectException("déplacement impossible y");
            }
        }
    }

    public void seDeplacer(Grille t,int xnew, int ynew, int f)throws DeplacementIncorrectException, CoordonneesIncorrectesException, CaseNonPleineException{
        /**
        * Déplace l'agent dans la grille vers de nouvelles coordonnées.
        *
        * @param t La grille.
        * @param xnew La nouvelle coordonnée x.
        * @param ynew La nouvelle coordonnée y.
        * @param f (la force) utilisé si un gardien est présent dans le nouveau cas.
        * @throws DeplacementIncorrectException Si les nouvelles coordonnées sont hors limites.
        * @throws CoordonneesIncorrectesException de la class Grille.
        * @throws CaseNonPleineException de la class Grille.
        */
        if (xnew < t.nbColonnes && ynew < t.nbLignes){
            x = xnew;
            y = ynew;

            if (t.caseEstVide(xnew, ynew))
                return;

            Contenu contenuCase = t.getCase(xnew, ynew);

            if (contenuCase instanceof Gardien){
                Gardien g = (Gardien)contenuCase;
                int pts = g.getPtVie();
                if (pts <= f){
                     	t.videCase(xnew, ynew);
                }
                else{
                    sac.clear();
                    g.setPtVie(pts - f);
                }

            }
            else if (contenuCase instanceof Joyau){
                sac.add((Joyau)(t.videCase(xnew, ynew)));
            }
        }

        else{
            if (xnew < t.nbColonnes){
                throw new DeplacementIncorrectException("déplacement impossible x");
            }
            else{
                throw new DeplacementIncorrectException("déplacement impossible y");
            }
        }
    }

    public int fortune(){
        /**
        * Calcule la fortune totale en additionnant les prix de tous les Joyaux dans le sac.
        *
        * @return La fortune totale.
        */
        int fort = 0;
        for (int i = 0; i < sac.size(); i++) {
             fort += (sac.get(i)).getPrix();
        }
        return fort;
    }

    public String contenuSac(){
        /**
        * Retourne le contenu du sac sous forme de chaîne de caractères.
        *
        * @return Le contenu du sac.
        */
        String s="";
        for (Joyau joyau : sac) {
            s += joyau.getType() + " ";
        }
        return s;
    }

    public String toString(){
        return String.format("Agent1 (%d, %d) sac[%s] fortune : %d", x, y, contenuSac(), fortune());
    }
}
