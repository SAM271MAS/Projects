import java.util.ArrayList;

public class TestSimulation{
    public static void main(String[] args)throws CaseNonPleineException{
        Grille t = new Grille (4,5);

        Agent1 a = new Agent1(0, 0);

        ArrayList<Contenu> c = new ArrayList<>();

        Gardien g1 = new Gardien("Gardien1", 1);
        Gardien g2 = new Gardien("Gardien2", 1);
        Gardien g3 = new Gardien("Gardien3", 1);

        Joyau j1 = new Joyau("Joyau1", 1);
        Joyau j2 = new Joyau("Joyau2", 1);
        Joyau j3 = new Joyau("Joyau3", 1);

        c.add(g1);
        c.add(g2);
        c.add(g3);

        c.add(j1);
        c.add(j2);
        c.add(j3);


        Simulation s = new Simulation(t, a, c);

        s.lance(10);
        s.lanceLog(5);
    }
}
