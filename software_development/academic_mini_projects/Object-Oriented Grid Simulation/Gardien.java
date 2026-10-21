public class Gardien extends Contenu{
    private int ptVie;

    //Constructeur
    public Gardien(String type, int quantite){
        super(type, quantite);
        ptVie = (int) (Math.random() * 201);
    }

    //Accesseurs
    public int getPtVie(){
        return ptVie;
    }

    //Mutateurs
    public void setPtVie(int ptVie){
        this.ptVie = ptVie;
    }


    public String toString(){
        String str = super.toString();
        if (!str.contains("n'est"))
            str += " pts de Vie : " + Integer.toString(ptVie);

        return str;
    }

}
