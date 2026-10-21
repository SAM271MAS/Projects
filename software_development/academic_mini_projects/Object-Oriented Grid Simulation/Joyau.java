public class Joyau extends Contenu{

    private int prix;

    //Constructeur
    public Joyau(String type, int quantite){
        super(type, quantite);
        prix = (int) (Math.random() * 1000) + 1;

    }

    //Accesseurs
    public String getType(){
        return type;
    }
    public int getPrix(){
        return prix;
    }

    public String toString(){
        String str = super.toString();
        if (!str.contains("n'est"))
            str += " fortune : " + Integer.toString(prix);

        return str;
    }


}
