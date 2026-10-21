import java.util.ArrayList;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

public class Simulation{

    private Grille t;
    private Agent1 a;
    private ArrayList<Contenu> m = new ArrayList<>();
    
    //Constructeur
    public Simulation(Grille t, Agent1 a, ArrayList<Contenu> m){
        this.t = t;
        this.a = a;
        this.m = m;

        int i = 0;
        while (i < m.size()) {
            int x = (int)(Math.random() * t.nbLignes);
            int y = (int)(Math.random() * t.nbColonnes);
            try {
                if (t.caseEstVide(x, y)){
                    t.setCase(x, y, m.get(i));
                    i++;
                }
            }
            catch (CoordonneesIncorrectesException e) {
                System.out.println("Erreur: "+e.getMessage());
            }
        }
    }

    public String toString(){
        String s = t.toString() + "\n" + a.toString() + "\n";
        s += "Liste de tous les Contenus présents actuellement:\n";
        for (Contenu c : m) {
            s += c.toString();
            s += "\n";
        }    
        return s;
    }

    public void lance(int nbEtapes)throws CaseNonPleineException{
        /**
        * Exécute la simulation pour un nombre d'étapes donné et affiche les informations de chaque étape de la simulation.
        *
        * @param nbEtapes Le nombre d'étapes de la simulation.
        * @throws CaseNonPleineException de la classe Grille.
        */
        String RED = "\u001B[31m";
        String RESET = "\u001B[0m";
        int i = 0;
        a.setX(0);
        a.setY(0);
        System.out.println("simulation : "+ i);
        t.affiche(2);
        System.out.println(toString());
        while(nbEtapes > 0){
            int x, y;

            try {
                x = (int)(Math.random() * 3) - 1;
                y = (int)(Math.random() * 3) - 1;

                if (Math.random() <= 0.7){
                    a.seDeplacer(t, a.getX()+x, a.getY()+y);
                }
                else{
                    int f = (int)(Math.random() * (100 - 10 + 1) + 10);
                    a.seDeplacer(t, a.getX()+1, a.getY()+1, f);
                }
                nbEtapes--;
                i++;
                System.out.println("simulation : "+ i);
                t.affiche(2);
                System.out.println(toString());
            }
            // Exception levée lorsque le déplacement est hors limite.
            // Réinitialisation des coordonnées de l'agent au centre de la grille.
            catch (DeplacementIncorrectException e) {
                x = (int)(t.nbColonnes / 2);
                y = (int)(t.nbLignes / 2);
                a.setX(x);
                a.setY(y);
                System.out.printf(RED + "simulation : %d\n", i + 1);
                System.out.println("Erreur: "+e.getMessage());
                System.out.printf("Relance de l'étape %d\n \n" + RESET, (i + 1));
            }

            // Exception levée lorsque les coordonnées sont incorrectes.
            // Réinitialisation des coordonnées de l'agent au centre de la grille.
            catch (CoordonneesIncorrectesException e) {
                x = (int)(t.nbColonnes / 2);
                y = (int)(t.nbLignes / 2);
                a.setX(x);
                a.setY(y);
                System.out.printf(RED + "simulation : %d\n", i + 1);
                System.out.println("Erreur: "+e.getMessage());
                System.out.printf("Relance de l'étape %d\n \n" + RESET, (i + 1));
            }
        }
    }
    public void lanceLog(int nbEtapes) throws CaseNonPleineException {
        /**
        * Exécute la simulation pour un nombre d'étapes donné et enregistre les informations de chaque étape de la simulation.
        *
        * @param nbEtapes Le nombre d'étapes de la simulation.
        * @throws CaseNonPleineException de la classe Grille.
        */
        Scanner scanner = new Scanner(System.in);

        // permettre à l'utilisateur d'entrer le nom du fichier dans lequel enregistrer le log
        System.out.print("Entrez le nom du fichier pour enregistrer le log : ");
        String fileName = scanner.nextLine();

        String RED = "\u001B[31m";
        String RESET = "\u001B[0m";
        int i = 0;
        a.setX(0);
        a.setY(0);
        StringBuilder logBuilder = new StringBuilder();
        logBuilder.append("simulation : ").append(i).append("\n");
        logBuilder.append(toString()).append("\n");

        while (nbEtapes > 0) {
            int x = 0;
            int y = 0;

            try {
                x = (int)(Math.random() * 3) - 1;
                y = (int)(Math.random() * 3) - 1;

                if (Math.random() <= 0.7){
                    a.seDeplacer(t, a.getX() + x, a.getY() + y);
                }
                else{
                    int f = (int) (Math.random() * (100 - 10 + 1) + 10);
                    a.seDeplacer(t, a.getX() + 1, a.getY() + 1, f);
                }
                nbEtapes--;
                i++;
                logBuilder.append("simulation : ").append(i).append("\n");
                logBuilder.append(toString()).append("\n");
            }

            // Exception levée lorsque le déplacement est hors limite.
            // Réinitialisation des coordonnées de l'agent au centre de la grille.
            catch (DeplacementIncorrectException e) {
                x = (int)(t.nbColonnes / 2);
                y = (int)(t.nbLignes / 2);
                a.setX(x);
                a.setY(y);
                logBuilder.append(RED + "Erreur: ").append(e.getMessage()).append("\n");
                logBuilder.append(String.format("Relance de l'étape %d\n \n" + RESET,(i + 1)));
            }

            // Exception levée lorsque les coordonnées sont incorrectes.
            // Réinitialisation des coordonnées de l'agent au centre de la grille.
            catch (CoordonneesIncorrectesException e) {
                x = (int)(t.nbColonnes / 2);
                y = (int)(t.nbLignes / 2);
                a.setX(x);
                a.setY(y);
                logBuilder.append(RED + "Erreur: ").append(e.getMessage()).append("\n");
                logBuilder.append(String.format("Relance de l'étape %d\n \n" + RESET, (i + 1)));
            }
        }
        writeLogToFile(fileName, logBuilder.toString());
    }
/**

    */
    private void writeLogToFile(String fileName, String logContent) {
        /**
        * Écrit le contenu du log dans un fichier spécifié.
        *
        * @param fileName Le nom du fichier dans lequel enregistrer le log.
        * @param logContent Le contenu du log à écrire dans le fichier.
        *
        */
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            writer.write(String.format("NOM : n\nPRENOM : nn\nGROUPE : nnn\n\n"));
            writer.write(logContent);
            String GREEN = "\u001B[32m";
            String RESET = "\u001B[0m";
            System.out.printf(GREEN + "Enregistré dans le fichier %s\n" + RESET, fileName);
        } catch (IOException e) {
            System.out.println("Erreur: IOE" + e.getMessage());
        }
    }
}

