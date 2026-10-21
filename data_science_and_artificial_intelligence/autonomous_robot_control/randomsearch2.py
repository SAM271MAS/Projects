from robot import *
import math, random
from copy import deepcopy

nb_robots = 0
debug = False

class Robot_player(Robot):
    team_name = "randomsearcher2"
    robot_id = -1
    iteration = 0

    param = []              # Paramètres du perceptron
    bestParam = []          # [score_cumulé, paramètres, numéro_du_trial]
    it_per_evaluation = 400
    trial = 0
    evaluations_per_param = 3
    current_behavior_score = 0
    evals_done = 0

    x_0 = 0
    y_0 = 0
    theta_0 = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=500, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        self.x_0, self.y_0, self.theta_0 = x_0, y_0, theta_0
        self.param = [random.randint(-1, 1) for _ in range(8)]
        self.it_per_evaluation = it_per_evaluation
        self.evaluations = evaluations
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
        self.score = 0

    def reset(self):
        super().reset()
        self.theta = random.randint(0, 360)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # Évaluation toutes les it_per_evaluation itérations
        if self.iteration % self.it_per_evaluation == 0:
            current_eval_score = self.log_sum_of_translation * (1 - abs(self.log_sum_of_rotation))
            self.current_behavior_score += current_eval_score
            self.evals_done += 1
            print(f"Essai {self.trial+1}, évaluation {self.evals_done} -> Score : {current_eval_score}")

            if self.evals_done >= self.evaluations_per_param:
                print(f"Score total du comportement {self.trial+1} = {self.current_behavior_score}")
                if self.trial == 0 or self.current_behavior_score > self.bestParam[0]:
                    self.bestParam = [self.current_behavior_score, deepcopy(self.param), self.trial]
                    print("Nouveau meilleur comportement trouvé!")
                self.trial += 1
                if self.trial < self.evaluations:
                    self.param = [random.randint(-1, 1) for _ in range(8)]
                self.current_behavior_score = 0
                self.evals_done = 0

            self.score = 0
            self.iteration += 1
            self.reset()
            return 0, 0, True

        # Phase d'exploitation : on rejoue le meilleur comportement
        if self.trial >= self.evaluations:
            self.param = self.bestParam[1]
            if (self.iteration - self.evaluations * self.it_per_evaluation) % 1000 == 0:
                self.score += self.log_sum_of_translation * (1 - abs(self.log_sum_of_rotation))
                print(f"Iteration : {self.iteration}")
                print(f"Meilleur comportement : {self.bestParam}")
                print(f"Score (exploitation) : {self.score}")
                self.reset()
                self.score = 0

        translation = math.tanh(
            self.param[0] +
            self.param[1] * sensors[sensor_front_left] +
            self.param[2] * sensors[sensor_front] +
            self.param[3] * sensors[sensor_front_right]
        )
        rotation = math.tanh(
            self.param[4] +
            self.param[5] * sensors[sensor_front_left] +
            self.param[6] * sensors[sensor_front] +
            self.param[7] * sensors[sensor_front_right]
        )

        if debug and self.iteration % 100 == 0:
            print(f"Robot {self.robot_id} à l'étape {self.iteration} - Capteurs : {sensors}")

        self.iteration += 1
        return translation, rotation, False

