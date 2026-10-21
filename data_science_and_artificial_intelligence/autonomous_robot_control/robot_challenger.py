import math
import random
from robot import * 
import robot_braitenberg_avoider
import robot_braitenberg_hateWall
import robot_subsomption

nb_robots = 0

class Robot_player(Robot):

    team_name = "Challenger"
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

        self.iteration = 0 # Added

    def braitenberg_optimisé(self, sensors, sensor_view, sensor_robot, sensor_team):
        # --- Fonctions auxiliaires pour encoder/décoder l'état et les paramètres candidats ---
        # On définit des moduli fixes pour chaque champ :
        mod_trial    = 1000      # trial : 3 chiffres
        mod_best_fit = 10000000  # best_fit : 7 chiffres
        mod_cp       = 10000     # candidat courant : 4 chiffres
        mod_bp       = 10000     # meilleur candidat : 4 chiffres
        mod_xstart   = 1000000   # x de référence : 6 chiffres
        mod_ystart   = 1000000   # y de référence : 6 chiffres
        mod_it       = 100       # itérations (on suppose it < 100)

        # Codage de l'état dans l'ordre : it, trial, best_fit, cp, bp, xstart, ystart
        def encode_state(it, trial, best_fit, cp, bp, xstart, ystart):
            return ((((( (it * mod_trial + trial) * mod_best_fit + best_fit)
                      * mod_cp + cp) * mod_bp + bp) * mod_xstart + xstart) * mod_ystart + ystart)

        def decode_state(mem):
            ystart = mem % mod_ystart
            mem //= mod_ystart
            xstart = mem % mod_xstart
            mem //= mod_xstart
            bp = mem % mod_bp
            mem //= mod_bp
            cp = mem % mod_cp
            mem //= mod_cp
            best_fit = mem % mod_best_fit
            mem //= mod_best_fit
            trial = mem % mod_trial
            mem //= mod_trial
            it = mem  # reste (doit être < mod_it)
            return it, trial, best_fit, cp, bp, xstart, ystart

        def encode_params(param_list):
            """Encode une liste de 8 paramètres (dans {-1, 0, 1}) en un entier en base 3."""
            cp_val = 0
            mapping = { -1: 0, 0: 1, 1: 2 }
            for p in param_list:
                cp_val = cp_val * 3 + mapping[p]
            return cp_val

        def decode_params(cp_val):
            """Décode un entier (base 3) en une liste de 8 paramètres (dans {-1, 0, 1})."""
            digits = [0] * 8
            for i in range(8):
                digits[7 - i] = cp_val % 3
                cp_val //= 3
            mapping = { 0: -1, 1: 0, 2: 1 }
            return [mapping[d] for d in digits]

        def mutate_params(param_list):
            """Muter aléatoirement un paramètre en remplaçant sa valeur par l'une des deux autres possibles."""
            idx = random.randint(0, 7)
            current = param_list[idx]
            allowed = [-1, 0, 1][:]
            allowed.remove(current)
            new_val = random.choice(allowed)
            new_params = param_list[:]  # copie de la liste
            new_params[idx] = new_val
            return new_params
        # --- Fin des fonctions auxiliaires ---

        # Initialisation de l'état persistant dans self.memory si non défini (self.memory == 0)
        # On stocke : it=0, trial=0, best_fit=0, cp = candidat aléatoire, bp = cp, et
        # xstart = self.x0 * 100, ystart = self.y0 * 100 (pour conserver deux décimales)
        if self.memory == 0:
            it = 0
            trial = 0
            best_fit = 0
            init_params = [random.randint(-1, 1) for _ in range(8)]
            cp = encode_params(init_params)
            bp = cp
            xstart = int(round(self.x0 * 100))
            ystart = int(round(self.y0 * 100))
            self.memory = encode_state(it, trial, best_fit, cp, bp, xstart, ystart)

        # Décodage de l'état depuis self.memory
        it, trial, best_fit, cp, bp, xstart, ystart = decode_state(self.memory)

        # --- Phase d'évaluation (toutes les 50 itérations) ---
        if it > 0 and it % 50 == 0:
            # Calcul de la fitness comme distance parcourue depuis le point de référence (xstart, ystart)
            fitness = math.sqrt((self.x - (xstart / 100.0))**2 + (self.y - (ystart / 100.0))**2)
            fitness_int = int(round(fitness * 1000))  # conservation de trois décimales

            # Si le candidat courant est supérieur, on met à jour le meilleur candidat et la meilleure fitness
            if fitness_int > best_fit:
                best_fit = fitness_int
                bp = cp

            # Générer un nouveau candidat par mutation du meilleur candidat
            best_candidate = decode_params(bp)
            new_candidate = mutate_params(best_candidate)
            cp = encode_params(new_candidate)

            trial += 1
            # Mise à jour du point de référence pour l'évaluation suivante (position actuelle)
            xstart = int(round(self.x * 100))
            ystart = int(round(self.y * 100))
            it += 1
        else:
            it += 1

        # --- Phase de contrôle : calcul des commandes de déplacement ---
        # 1. Comportement issu du candidat génétique
        current_params = decode_params(cp)
        genetic_translation = math.tanh(
             current_params[0] +
             current_params[1] * sensors[sensor_front_left] +
             current_params[2] * sensors[sensor_front] +
             current_params[3] * sensors[sensor_front_right]
        )
        genetic_rotation = math.tanh(
             current_params[4] +
             current_params[5] * sensors[sensor_front_left] +
             current_params[6] * sensors[sensor_front] +
             current_params[7] * sensors[sensor_front_right]
        )

        # 2. Comportement d'évitement de murs « Braitenberg »
        # On remplit sensor_to_wall en considérant que seuls les capteurs détectant un mur (sensor_view == 1)
        # renvoient une valeur significative ; sinon, on suppose le monde vide (valeur 1.0).
        sensor_to_wall = [sensors[i] if sensor_view[i] == 1 else 1.0 for i in range(8)]
        # Pour favoriser l'avance en ligne droite, on définit un seuil pour le capteur frontal.
        threshold = 0.7  # si le capteur frontal indique une distance supérieure au seuil, on considère le chemin libre
        if sensors[sensor_front] > threshold:
             wall_translation = 1.0   # avancer à vitesse maximale
             wall_rotation = 0.0        # aucune rotation
        else:
             wall_translation = sensors[sensor_front] * 0.5  # avancer plus lentement en cas d'obstacle
             # La rotation est déterminée par la différence entre les capteurs latéraux.
             wall_rotation = ( (1 - sensor_to_wall[sensor_front_right]) 
                               - (1 - sensor_to_wall[sensor_front_left]) )

        # 3. Combinaison des deux comportements grâce à une moyenne pondérée
        alpha = 0.5  # poids du comportement génétique
        beta = 0.5   # poids du comportement d'évitement
        translation = alpha * genetic_translation + beta * wall_translation
        rotation = alpha * genetic_rotation + beta * wall_rotation

        # Mise à jour de self.memory (on garde it modulo mod_it pour éviter le débordement)
        self.memory = encode_state(it % mod_it, trial, best_fit, cp, bp, xstart, ystart)

        return translation, rotation, False

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        if self.robot_id == 0:
            return self.braitenberg_optimisé(sensors, sensor_view, sensor_robot, sensor_team)
        elif self.robot_id == 1:
            return robot_braitenberg_avoider.Robot_player.step(self, sensors, sensor_view, sensor_robot, sensor_team)
        elif self.robot_id == 2:
            return robot_braitenberg_avoider.Robot_player.step(self, sensors, sensor_view, sensor_robot, sensor_team)
        elif self.robot_id == 3:
            return robot_subsomption.Robot_player.step(self, sensors, sensor_view, sensor_robot, sensor_team)
        else:
            translation = sensors[sensor_front]
            rotation = 1.0 * sensors[sensor_front_left] - 1.0 * sensors[sensor_front_right] + (random.random()-0.5)*0.1
            return translation, rotation, False
