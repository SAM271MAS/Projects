package algorithms;

import robotsimulator.Brain;
import characteristics.Parameters;
import characteristics.IRadarResult;
import java.util.ArrayList;

public class TeamSamMainBot extends Brain {

    //  Etats grafcet 
    private static final int ALIGN_TASK  = 1;
    private static final int ENGAGE_TASK = 2;

    //  Constantes 
    // Tolérance angulaire pour valider l'alignement sur une cible
    private static final double HEADING_PRECISION = 0.05; 
    // Fréquence de déplacement (avancer tous les N ticks) en mode patrouille
    private static final int MOVE_EVERY_N = 3;

    // Paramètres de balayage : oscillation du tir autour de la direction par défaut
    // Utilisé lorsque le robot n'a aucune cible validée (Priorité 3)
    private static final double SWEEP_MAX  = 0.3;  // Amplitude max (~17 degrés de chaque côté)
    private static final double SWEEP_STEP = 0.01; // Incrément angulaire par itération (vitesse de balayage)

    //  Variables d'etat
    private int    state;           // Étape active du Grafcet
    private int    moveCounter;     // Compteur pour cadencer le déplacement sans bloquer le tir
    private int    initialDelay;    // Temporisation de sécurité au spawn (éviter le friendly fire)

    private double defaultDirection; // Cap de base assigné au robot
    private double targetAngle;      // Angle de la cible actuelle (vers où s'orienter)
    private double fireAngle;        // Angle de la tourelle (vers où tirer)

    // Variables liées à l'état du balayage (oscillation)
    private double sweepOffset;      // Décalage actuel par rapport à la direction par défaut
    private int    sweepDirection;   // Sens du balayage (+1 ou -1)

    public TeamSamMainBot() { super(); }

    /**
     * Étape 0 (Initialisation).
     * Exécutée une seule fois au déploiement du robot.
     */
    public void activate() {
        state            = ALIGN_TASK;
        moveCounter      = 0;
        initialDelay     = 100;
        defaultDirection = getHeading();
        targetAngle      = defaultDirection;
        fireAngle        = defaultDirection;
        sweepOffset      = 0;
        sweepDirection   = 1;
        sendLogMessage("Active.");
    }

    public void step() {

        if (initialDelay > 0) initialDelay--;

        // Evaluation des priorités
        int currentPriority = 3; // Niveau de base : 1=Radar propre, 2=Radar allié, 3=Par défaut (Balayage)

        // Priorité 1 : Détection directe au radar (Priorité absolue)
        for (IRadarResult r : detectRadar()) {
            if (isEnemy(r)) {
                targetAngle     = r.getObjectDirection();
                fireAngle       = r.getObjectDirection();
                currentPriority = 1;
                // Partage de la cible avec l'essaim
                broadcast("MAIN_TARGET:" + targetAngle);
                break;
            }
        }

        // Priorité 2 : Écoute du réseau de l'essaim (Si aucune cible directe n'est vue)
        if (currentPriority > 1) {
            ArrayList<String> messages = fetchAllMessages();
            for (String msg : messages) {
                if (msg.startsWith("MAIN_TARGET:") && currentPriority > 2) {
                    targetAngle     = Double.parseDouble(msg.split(":")[1]);
                    fireAngle       = targetAngle;
                    currentPriority = 2; // Bascule sur la cible désignée par un allié
                }
            }
        }

        // Priorité 3 : Aucune cible (Mode patrouille et balayage de zone)
        if (currentPriority == 3) {
            targetAngle = defaultDirection;

            // Avancement de l'oscillateur de balayage pour couvrir une zone de tir
            sweepOffset += sweepDirection * SWEEP_STEP;
            if (sweepOffset >  SWEEP_MAX) { sweepOffset =  SWEEP_MAX; sweepDirection = -1; }
            if (sweepOffset < -SWEEP_MAX) { sweepOffset = -SWEEP_MAX; sweepDirection =  1; }

            fireAngle = defaultDirection + sweepOffset;
        } else {
            // Réinitialisation du balayage pour qu'il soit centré lors de la prochaine perte de cible
            sweepOffset    = 0;
            sweepDirection = 1;
        }

        if (initialDelay == 0) {
            fire(fireAngle);
        }

        // Etat 1
        if (state == ALIGN_TASK) {
            if (isHeading(targetAngle)) {
                state = ENGAGE_TASK;
            } else {
                stepTurn(getTurnDirection(targetAngle));
            }
            return;
        }

        // Etat 2
        if (state == ENGAGE_TASK) {
            if (!isHeading(targetAngle)) {
                state = ALIGN_TASK;
                stepTurn(getTurnDirection(targetAngle));
            } else {
                moveCounter++;
                
                int requiredSteps = (currentPriority < 3) ? 2 : MOVE_EVERY_N;
                
                if (moveCounter >= requiredSteps) {
                    move();
                    moveCounter = 0;
                }
            }
            return;
        }
    }

    //  Fonctions Helpers

    /**
     * Vérifie si l'entité détectée au radar est un robot ennemi.
     */
    private boolean isEnemy(IRadarResult r) {
        return r.getObjectType() == IRadarResult.Types.OpponentMainBot
            || r.getObjectType() == IRadarResult.Types.OpponentSecondaryBot;
    }

    /**
     * Détermine si le cap actuel du robot est aligné avec la direction cible, 
     * en prenant en compte la tolérance définie.
     */
    private boolean isHeading(double dir) {
        return Math.abs(Math.sin(getHeading() - dir)) < HEADING_PRECISION;
    }

    /**
     * Normalise un angle pour le maintenir dans l'intervalle ]-Pi, Pi].
     */
    private double normalizeAngle(double angle) {
        while (angle <= -Math.PI) angle += 2 * Math.PI;
        while (angle >   Math.PI) angle -= 2 * Math.PI;
        return angle;
    }

    /**
     * Calcule le sens de rotation (Gauche/Droite) le plus court pour atteindre une cible.
     */
    private Parameters.Direction getTurnDirection(double targetDir) {
        double diff = normalizeAngle(targetDir - getHeading());
        return (diff > 0) ? Parameters.Direction.RIGHT : Parameters.Direction.LEFT;
    }
}
