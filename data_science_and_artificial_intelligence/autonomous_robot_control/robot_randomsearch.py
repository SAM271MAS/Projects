from robot import * 
import math
from copy import deepcopy
from random import randint

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "randomsearcher"
    robot_id = -1
    iteration = 0

    param = []
    bestParam = []
    it_per_evaluation = 400
    trial = 0

    x_0 = 0
    y_0 = 0
    theta_0 = 0 # in [0,360]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        self.param = [randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

        self.score = 0
        self.evaluations = evaluations

    def reset(self):
        super().reset()
        self.theta = randint(0, 360)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        if self.iteration % self.it_per_evaluation == 0:

            if self.trial < self.evaluations:

                self.score = self.log_sum_of_translation*(1-abs(self.log_sum_of_rotation))
                if self.trial == 0:
                    self.bestParam = deepcopy([self.score]) + [deepcopy(self.param)] + [deepcopy(self.trial)]
                elif self.bestParam[0] < self.score:
                    self.bestParam = deepcopy([self.score]) + [deepcopy(self.param)] + [deepcopy(self.trial)]

                if self.iteration > 0:
                    print ("\tparameters           =",self.param)
                    print ("\ttranslations         =",self.log_sum_of_translation,"; rotations =",self.log_sum_of_rotation) # effective translation/rotation
                    print ("\tdistance from origin =",math.sqrt((self.x-self.x_0)**2+(self.y-self.y_0)**2))

                    print ("\tscore                =",self.score)

                if self.iteration % (self.it_per_evaluation*3) == 0:

                    self.param = [randint(-1, 1) for i in range(8)]
                    self.trial = self.trial + 1

                print ("Trying strategy no.",self.trial)
                self.iteration = self.iteration + 1

                self.reset()
                self.score = 0

                return 0, 0, True # ask for resetevaluations

        if self.trial >= self.evaluations:
            self.param = self.bestParam[1]
            if (self.iteration - self.evaluations*self.it_per_evaluation) % 1000 == 0 :
                self.score += self.log_sum_of_translation*(1-abs(self.log_sum_of_rotation))
                print ("iteration              :",self.iteration)
                print ("\tbest_param           :",self.bestParam)
                print ("\tparameters           =",self.param)
                print ("\ttranslations         =",self.log_sum_of_translation,"; rotations =",self.log_sum_of_rotation) # *effective* translation/rotation (ie. measured from displacement)
                print ("\tdistance from origin =",math.sqrt((self.x-self.x_0)**2+(self.y-self.y_0)**2))
                print ("\tscore                =",self.score)
                self.reset()
                self.score = 0

        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (team "+str(self.team_name)+")","at step",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                print ("\ttype (0:empty, 1:wall, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1

        return translation, rotation, False
