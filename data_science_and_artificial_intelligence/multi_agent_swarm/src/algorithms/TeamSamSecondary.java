package algorithms;

import robotsimulator.Brain;
import characteristics.Parameters;


public class TeamSamSecondary extends Brain {

    //  Variables statics
    private static int counterEast = 0;
    private static int counterWest = 0;

    //  Variables d'instance
    private boolean deployed = false; 
    private int     deployCounter;
    private double  wallAngle;

    public TeamSamSecondary() { super(); }

    /**
     * Phase d'initialisation et de calcul de la trajectoire.
     * Exécutée une seule fois au "spawn" du robot.
     */
    public void activate() {
        // Détermination du côté d'apparition (Est ou Ouest) pour utiliser le bon compteur
        if (getHeading() == Parameters.EAST) {
            wallAngle = (counterEast % 2 == 0) ? Parameters.NORTH : Parameters.SOUTH;
            counterEast++;
            if (counterEast >= 2) counterEast = 0;
        } else {
            wallAngle = (counterWest % 2 == 0) ? Parameters.NORTH : Parameters.SOUTH;
            counterWest++;
            if (counterWest >= 2) counterWest = 0;
        }

        deployCounter = 700; 
    }

    /**
     * Boucle de contrôle principale
     */
    public void step() {
        if (deployed) return; 

        if (!isHeading(wallAngle)) {
            stepTurn(getTurnDirection(wallAngle));
        } 
        else {
            move();
            if (--deployCounter <= 0) deployed = true;
        }
    }

    // Fonctions Helpers

    /**
     * Évalue si le cap actuel correspond à la consigne (dir), 
     * avec une tolérance angulaire de 0.05 radian pour éviter les oscillations
     */
    private boolean isHeading(double dir) {
        return Math.abs(Math.sin(getHeading() - dir)) < 0.05;
    }

    /**
     * Borne la valeur d'un angle dans l'intervalle ]-Pi, Pi] 
     * pour garantir des calculs de trajectoire optimisés
     */
    private double normalizeAngle(double angle) {
        while (angle <= -Math.PI) angle += 2 * Math.PI;
        while (angle >   Math.PI) angle -= 2 * Math.PI;
        return angle;
    }

    /**
     * Détermine le chemin de rotation le plus court (horaire ou anti-horaire)
     * pour rejoindre le cap cible
     */
    private Parameters.Direction getTurnDirection(double targetDir) {
        double diff = normalizeAngle(targetDir - getHeading());
        return (diff > 0) ? Parameters.Direction.RIGHT : Parameters.Direction.LEFT;
    }
}
