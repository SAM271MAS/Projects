# -*- coding: utf-8 -*-

# Nicolas, 2024-02-09
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys, os
from itertools import chain
import matplotlib.pyplot as plt


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme
from search import grid2D


class Joueur():

    occupations_restos = [0 for _ in range(5)] # 5 = nb restaurants
    occupations_restos_tmp = [0 for _ in range(5)]

    def __init__(self, player):
        self.player = player # L'objet spirite
        self.path = [] # La liste de cases qui lui reste a parcourir

        # La strategie de base (celle de tetu et stochastique)
        self.strat = self.strat_tetu_stochastique 
        # Le restaurant aleatoire de la strategie stochastique
        self.set_choix_resto([]) 
        
        # Utilise seulement pour la strategie greedy_min
        self.cap_restos = [-1 for _ in range(nb_restos)] 

        # Regrets accumulés pour chaque restaurant (pour la strategie regret matching)
        self.regrets = Joueur.occupations_restos.copy() # + [0] # pour le coupe_file

    def set_strat(self, strat):
        self.strat = strat.__get__(self, Joueur) # Pour lier la methode a l'instance en question

    def set_choix_resto(self, id_restaurant):
        """id_restaurant est une liste
        Doit valoir [] pour la strategie stochastique et coupe_files
        Doit valoir [x] pour la strategie tetue ou x € [0, nb_restos-1]
        Doit valoir [x0, x1, ..., xn] pour les autres strategies avec i € [0, nb_restos-1]"""

        self.choix_resto = id_restaurant if id_restaurant else [random.randint(0, nb_restos - 1)]

    def get_next_move(self):
        if not self.path:
            self.path = self.strat()
    
        path = self.path[0] if type(self.path) == list else self.path
        self.path = self.path[1:] if type(self.path) == list else []

        return path # Le couple du prochain coup


    #-------------------------------
    # Fonctions pour les differentes strategies
    #-------------------------------

    def get_path(self, pos_src, pos_dst):
        # Renvoie le plus court chemin de src a dst

        if pos_src == pos_dst:
            return pos_src
        else:
            return probleme.astar(ProblemeGrid2D(pos_src, pos_dst, g, 'manhattan'))


    def strat_tetu_stochastique(self):
        # Strategie tetu ou stochastique
        # On va toujours dans le meme restaurant ou un aléatoire

        return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]])

    def strat_greedy(self):
        # Strategie Greedy min
        # On parcours dans l'ordre croissant (0->1->2..->nb_restos-1)
        seuil = 3

        if self.choix_resto[0] >= nb_restos: # On a teste tous les resturants
            return self.player.get_rowcol() # On abandonne et on reste au meme endroit pour eviter les longues iterations

        elif self.player.get_rowcol() in pos_restaurants: # On se trouve dans un restaurant
            if nb_players_in_resto(self.choix_resto[0]) > seuil: # Si le seuil est depasse
                if self.choix_resto[1:] != []:
                    self.choix_resto = self.choix_resto[1:]
                    return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # On teste le prochain restaurant
                else:
                    self.choix_resto = [nb_restos] # Losqu'on teste le dernier restaurant on s'accorde un dernier trajet aleatoire
                    return self.get_path(self.player.get_rowcol(), pos_restaurants[random.randint(0, nb_restos - 1)])               
            else: # Sinon
                return self.player.get_rowcol() # On reste dans le meme restaurant
            
        else:
            return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # Si on est pas dans un restaurant 
        
    def strat_greedy_min(self):
        # Strategie Greedy
        # On parcours dans l'ordre croissant (0->1->2..->nb_restos-1)
        # Puis, une fois tous les resturants parcourus on va dans celui ou il y a le moins de personnes

        if self.choix_resto[0] >= nb_restos: # On a teste tous les restaurants
            # On va au restaurant ayant le minimum d'occupation
            occupation_resto = pos_restaurants.index(self.player.get_rowcol())
            if nb_players_in_resto(occupation_resto) > min(self.cap_restos): # Si le nombre d'occupation a change entre temps et que le minimum n'est plus le meme
                self.cap_restos[occupation_resto] = nb_players_in_resto(occupation_resto)
                return self.get_path(self.player.get_rowcol(), pos_restaurants[self.cap_restos.index(min(self.cap_restos))])
            else: # Si c'est toujours l'occupation minimum
                return self.player.get_rowcol() # On reste dans le meme restaurant

        elif self.player.get_rowcol() in pos_restaurants: # On se trouve dans un restaurant
            occupation_resto = pos_restaurants.index(self.player.get_rowcol()) # On note le nombre d'occupation
            self.cap_restos[occupation_resto] = nb_players_in_resto(occupation_resto)
            if self.choix_resto[1:] != []:
                self.choix_resto = self.choix_resto[1:]
                return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # On teste le prochain restaurant
            else:
                self.choix_resto = [nb_restos] # Losqu'on teste le dernier restaurant on va au minimum
                # On va au restaurant ayant le minimum d'occupation
                return self.get_path(self.player.get_rowcol(), pos_restaurants[self.cap_restos.index(min(self.cap_restos))])
            
        else:
            return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # Si on est pas dans un restaurant 
        
    def strat_coupe_files(self):
        # Strategie du coupe files
        # On cherche a imperativement recuperer le coupe files avant d'aller dans un restaurant aleatoire
        
        if len(self.player.inventory) > 0 or not coupe_files_set: # Si on a un coupe files ou qu'il n'y en a plus
            # Strategie tetu ou stochastique
            # On va toujours dans le meme restaurant ou un aléatoire

            return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]])
        
        else: # Si on a pas de coupe files
            distance_coupes_files = [grid2D.distManhattan(self.player.get_rowcol(), coupe_file) for coupe_file in coupe_files_set]
            closest_coupe_files = coupe_files_set[distance_coupes_files.index(min(distance_coupes_files))]
            return self.get_path(self.player.get_rowcol(), closest_coupe_files)
        
    def strat_coupe_files_greedy_min(self):
        # Strategies du coupe files et de greedy combinees
        # On va chercher un coupe file et on va dans le restaurant le moins occupe
        
        if len(self.player.inventory) > 0 or not coupe_files_set: # Si on a un coupe_file ou qu'il n'y en a plus
            # Strategie Greedy
            # On parcours dans l'ordre croissant (0->1->2..->nb_restos-1)
            # Puis, une fois tous les resturants parcourus on va dans celui ou il y a le moins de personnes

            if self.choix_resto[0] >= nb_restos: # On a teste tous les restaurants
                # On va au restaurant ayant le minimum d'occupation
                occupation_resto = pos_restaurants.index(self.player.get_rowcol())
                if nb_players_in_resto(occupation_resto) > min(self.cap_restos): # Si le nombre d'occupation a change entre temps et que le minimum n'est plus le meme
                    self.cap_restos[occupation_resto] = nb_players_in_resto(occupation_resto)
                    return self.get_path(self.player.get_rowcol(), pos_restaurants[self.cap_restos.index(min(self.cap_restos))])
                else: # Si c'est toujours l'occupation minimum
                    return self.player.get_rowcol() # On reste dans le meme restaurant

            elif self.player.get_rowcol() in pos_restaurants: # On se trouve dans un restaurant
                occupation_resto = pos_restaurants.index(self.player.get_rowcol()) # On note le nombre d'occupation
                self.cap_restos[occupation_resto] = nb_players_in_resto(occupation_resto)
                if self.choix_resto[1:] != []:
                    self.choix_resto = self.choix_resto[1:]
                    return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # On teste le prochain restaurant
                else:
                    self.choix_resto = [nb_restos] # Losqu'on teste le dernier restaurant on va au minimum
                    # On va au restaurant ayant le minimum d'occupation
                    return self.get_path(self.player.get_rowcol(), pos_restaurants[self.cap_restos.index(min(self.cap_restos))])
                
            else:
                return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]]) # Si on est pas dans un restaurant 
        
        else: # Si on a pas de coupe files
            distance_coupes_files = [grid2D.distManhattan(self.player.get_rowcol(), coupe_file) for coupe_file in coupe_files_set] # non vide par H
            closest_coupe_files = coupe_files_set[distance_coupes_files.index(min(distance_coupes_files))]
            return self.get_path(self.player.get_rowcol(), closest_coupe_files)
        
    def strat_fictitious_play(self):
        # Stratégie fictitious play.
        # La fréquentation des restaurants par les autres et choisit le restaurant
        # avec la plus faible fréquence historique. Historique stocke dans la variable statique occupations_restos
        # En cas d'égalité, il choisit aléatoirement parmi les restaurants minimaux
        
        if self.player.get_rowcol() in pos_restaurants:
            return self.player.get_rowcol() # Pour eviter de diverger

        else:
            # Trouver la (ou les) valeur(s) minimale(s) dans l'historique
            min_occ = min(Joueur.occupations_restos)
            # Récupérer les indices des restaurants dont l'historique est égal au minimum
            best_choices = [i for i, occ in enumerate(Joueur.occupations_restos) if occ == min_occ]

            # Choisir aléatoirement parmi les meilleures options
            r_choice = random.choice(best_choices)
            self.choix_resto = [r_choice]

            return self.get_path(self.player.get_rowcol(), pos_restaurants[r_choice])

    def strat_regret_matching(self):
        # Si le joueur est déjà à un restaurant, il reste sur place
        if self.player.get_rowcol() in pos_restaurants:
            return self.player.get_rowcol()
        else:
            # Obtenir l'occupation actuelle et la capacité des restaurants     
            occupation_actuelle = self.occupations_restos_tmp  # tmp représente l'occupation de chaque restaurant ce tour
            capacite = [1]*nb_restos # Capacite des restaurants fixe a 1
    
            # Estimer les gains pour chaque restaurant
            # Les gains sont la probabilité d'être servi, basée sur l'occupation et la capacité
            gains = [
                1 if occupation_actuelle[r] == 0 else min(1, capacite[r] / occupation_actuelle[r])
                for r in range(nb_restos)
            ]
    
            # Gain réel pour le restaurant choisi lors du tour précédent
            gain_reel = gains[self.choix_resto[0]]
    
            # Accumuler les regrets positifs pour tous les restaurants
            self.regrets = [
                self.regrets[r] + max(0, gain - gain_reel) for r, gain in enumerate(gains)
            ]
            regret_total = sum(self.regrets)
    
            print(f"gains : {gains}")
            print(f"regrets (cumulés) : {self.regrets}")
            print(f"regret total : {regret_total}")
    
            if regret_total > 0:
                # Probabilités proportionnelles aux regrets accumulés
                probabilites = [r / regret_total for r in self.regrets]
                choix_resto = np.random.choice(range(nb_restos), p=probabilites)
                print(f"probabilites : {probabilites}")
                print(f"choix_resto : {choix_resto}")
            else:
                # Distribution uniforme lorsque aucun regret n'est positif
                choix_resto = np.random.choice(range(nb_restos))
                print("Aucun regret - choix aléatoire.")
    
            self.choix_resto = [choix_resto]
    
            return self.get_path(self.player.get_rowcol(), pos_restaurants[self.choix_resto[0]])







#-------------------------------
# Fonctions permettant de récupérer les listes des coordonnées
# d'un ensemble d'objets ou de joueurs
#-------------------------------

def item_states(items):
    # donne la liste des coordonnees des items
    return [o.get_rowcol() for o in items]

def player_states(players):
    # donne la liste des coordonnees des joueurs
    return [p.get_rowcol() for p in players]

#-------------------------------
# Fonctions definissant les positions legales et placement aléatoire
#-------------------------------

def legal_position(pos):
    row,col = pos
    # une position legale est dans la carte et pas sur un objet deja pose ni sur un joueur ni sur un resto
    return ((pos not in item_states(coupe_files)) and (pos not in player_states(players)) and (pos not in pos_restaurants) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)

def draw_random_location():
    # tire au hasard un couple de positions permettant de placer un item
    while True:
        random_loc = (random.randint(lMin,lMax),random.randint(cMin,cMax))
        if legal_position(random_loc):
            return(random_loc)

def players_in_resto(r):
    """
    :param r: id of the resto
    :return: id of players in resto
    """
    are_here = []
    pos = pos_restaurants[r]
    for i in range(0,nb_players):
        if players[i].get_rowcol() == pos and joueurs[i].path == []: 
            # Si un joueur est arrive dans ce restaurant, 
            # et qu'il a finit son chemin, 
            if joueurs[i].strat == joueurs[i].strat_greedy_min:
                if joueurs[i].cap_restos[-1] != -1: # Si il n'a finit pas de visiter tous les resturants qu'il doit faire
                    are_here.append(i) # Le joueur joueurs[i] est alors juste de passage
            else:
                are_here.append(i)
    return are_here

def nb_players_in_resto(r):
    """
    :param r: id of resto
    :return: int number of players currently here
    """
    return len(players_in_resto(r))


#-------------------------------
# Fonction pour le calcul des scores
#-------------------------------

def get_score_per_day(players_in_resto, nb_restos, nb_players, capacity, players):
    restos_and_players = {r: players_in_resto(r) for r in range(nb_restos)}
    score_per_player = {pla: 0 for pla in range(nb_players)}

    # Des affichages pour verifier la validite du score
    # print(f"Repartition des joueurs a la fin de la journee: {restos_and_players}")
    # pla_coupe_files = {r: [pla for pla in players_in_resto(r) if len(players[pla].inventory) > 0] for r in range(nb_restos)}
    # print(f"Repartition des joueurs ayant des coupe_files: {pla_coupe_files}")

    for r in restos_and_players.keys():
        while len(restos_and_players[r]) > 0 and capacity[r] > 0:
            # Tant qu'il y a des gens a servir et que l'on peut servir

            prio = [pla for pla in restos_and_players[r] if len(players[pla].inventory) > 0]

            delivered_player = random.choice(prio) if prio else random.choice(restos_and_players[r])
            restos_and_players[r].remove(delivered_player)
            score_per_player[delivered_player] += 1
            capacity[r] -= 1

    # Affichage du score de la journée
    # print(f"Score de la journée = {score_per_player}")
    # print(f"Score de la journée = {list(score_per_player.values())}")

    return np.array(list(score_per_player.values()))

#-------------------------------
# Fonction pour la maj des strategies regret_matching et fictitious play
#-------------------------------

# def update_agent_data(occupations_restos):
#     # Met à jour l'historique et les regrets pour chaque joueur.
#     # Pour regret matching, si le joueur n'était pas dans le restaurant ayant le plus faible occupation,
#     # le regret est augmenté en fonction de la différence de gain potentielle.
#     # Pour fictitious play, on ajoute simplement l'attendance observée au tableau historique.

#     joueur_regret = None
#     for joueur in joueurs:
#         if joueur.strat == joueur.strat_regret_matching:
#             #current_gain = occupations_restos[joueur.choix_resto[0]]
#             current_gain = 1 if occupations_restos[joueur.choix_resto[0]] == 0 else 0
#             joueur_regret = joueur
            
#     for joueur in joueurs:
#         #if joueur.strat == joueur.strat_fictitious_play or joueur.strat == joueur.strat_regret_matching:
#         for r in range(nb_restos):
#             # Mise à jour de l'historique (fictitious play)
#             joueur.history[r] += occupations_restos[r]

#             # Mise a jour des regrets (regret matching)
#             if r != joueur.choix_resto[0]: # Les autres joueurs
#                 # Pour le regret matching, calculons le gain potentiel pour chaque action
#                 #potential_gain = occupations_restos[r]
#                 potential_gain = 1 if occupations_restos[r] == 0 else 0

#                 joueur_regret.regrets[r] += current_gain - potential_gain




def journee(is_update):

    #-------------------------------
    # On place tous les coupe_files du bord au hasard
    #-------------------------------
                    
    for o in coupe_files:
        (x1,y1) = draw_random_location()
        o.set_rowcol(x1,y1)
        coupe_files_set.append((x1, y1))
        game.mainiteration()

    #-------------------------------
    # On place tous les joueurs au hasard sur la ligne du bas
    #-------------------------------

    y_init = [3,5,7,9,11,13,15,17]
    x_init = 18
    random.shuffle(y_init)
    for i in range(0,nb_players):
        players[i].set_rowcol(x_init,y_init[i])
        game.mainiteration()

    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

    check_two_times = [] # On check deux fois (<=> deux tours) si tout le monde est satisfait dans son restaurant

    for i in range(iterations):
        
        are_arrived = [False for _ in range(nb_players)] # Condition d'arret pour terminer la partie plus rapidement
    
        for j in range(0,nb_players):
            (row, col) = joueurs[j].get_next_move()
    
            are_arrived[j] = joueurs[j].path == []  # Si apres ce coup on a plus d'autres cases a parcourir
                                                    # alors c'est qu'on est arrive
            if are_arrived[j] == False: # Si un joueur a encore des cases a parcourir
                check_two_times = [] # On reset le compteur de check pour re-checker 2 fois lorsqu'il sera arrive
    
            players[j].set_rowcol(row, col)
    
            if (row, col) in item_states(coupe_files):
                players[j].ramasse(game.layers) # Pour l'inventaire du joueur
                if (row, col) in coupe_files_set:
                    coupe_files_set.remove((row, col)) # Pour la strat coupe files
    
    
            # mise à jour du pleateau de jeu (a chaque deplacement d'un joueur)
            game.mainiteration()
    
        if all(are_arrived): # Si tous les joueurs sont arrives
            check_two_times.append(True) # On finit la journee
    
            if len(check_two_times) == 2: # Si on a bien verifie au moins deux fois que tous les joueurs sont satisfait
                break # On arrete la partie

    if i == iterations:
        print(f"Le nombre d'iterations etant trop petit, certains joueurs n'ont pas reussi a trouve un restaurant")

    # -------------------------------
    # Calcul des scores
    # -------------------------------

    # calcul du nombre de joueurs sur chaque resto

    # attendance = [0]*nb_restos
    for r in range(0,nb_restos):
    #    attendance[r]=nb_players_in_resto(r)
        Joueur.occupations_restos_tmp[r] += nb_players_in_resto(r)

    if is_update:
        Joueur.occupations_restos = Joueur.occupations_restos_tmp.copy()

    # calcul du service et points

    score_per_day = get_score_per_day(players_in_resto, nb_restos, nb_players, capacity.copy(), players)
    
    return score_per_day

    #-------------------------------





# os.environ["SDL_VIDEODRIVER"] = "dummy" # Pour cacher l'interface graphique
# Pour afficher l'interface graphique enlever le commentaire dans la boucle au niveau du game.mainiteration() et mettre en commmentaire la ligne au dessus

if __name__ == '__main__':
    # ---- ---- ---- ---- ---- ----
    # ---- Main                ----
    # ---- ---- ---- ---- ---- ----

    game = Game()

    def init(_boardname=None):
        global player, game
        name = _boardname if _boardname is not None else 'restaurant-map2'
        #game = Game('./Cartes/' + name + '.json', SpriteBuilder)
        game = Game('Cartes/' + name + '.json', SpriteBuilder)
        game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
        game.populate_sprite_names(game.O)
        game.fps = 60 # frames per second
        # player = game.player

    #for arg in sys.argv:
    iterations = 200 # nb de pas max par episode
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    #print(f"Iterations: {iterations}")


    # -----------------------------------------------
    nb_update = 1 # Nombre de maj au total pour regret et fictitious, >0, update une fois toutes les nb_days journees passees
    nb_days = 1 # Nombre de journees durant la partie
    assert nb_update <= nb_days and nb_days % nb_update == 0
    score_per_game = None

    for partie in range(nb_days):
        if nb_days >= 100:
            print(partie)
        
        init()
        nb_lignes = game.spriteBuilder.rowsize
        nb_cols = game.spriteBuilder.colsize
        assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
        lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker les objets)
        lMax=nb_lignes-2
        cMin=2
        cMax=nb_cols-2
        g = np.ones((nb_lignes, nb_cols), dtype=bool)  # une matrice remplie par defaut a True

        for i in range(nb_lignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nb_lignes - 1][i] = False
            g[nb_lignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nb_lignes - 1] = False
            g[i][nb_lignes - 2] = False


        players = [o for o in game.layers['joueur']]
        nb_players = len(players)

        pos_restaurants = [(3,4),(3,7),(3,10),(3,13),(3,16)] # 5 restaurants positionnes
        nb_restos = len(pos_restaurants)
        capacity = [1]*nb_restos # Capacite des restaurants fixe a 1

        coupe_files = [o for o in game.layers["ramassable"]] # a utiliser dans le cas de la variante coupe-file
        coupe_files_set = [] # Utile pour les strategies coupe_files 
        nb_coupe_files= len(coupe_files)


        joueurs = [Joueur(pla) for pla in players]

        joueurs[0].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[0].set_choix_resto([])
        joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[1].set_choix_resto([])

        joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[2].set_choix_resto([])
        
        joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[3].set_choix_resto([])

        joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[4].set_choix_resto([])

        joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[5].set_choix_resto([])

        joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
        joueurs[6].set_choix_resto([])

        joueurs[7].set_strat(Joueur.strat_greedy)
        joueurs[7].set_choix_resto([])





        res = journee((partie + 1) % (nb_days // nb_update) == 0)
        score_per_game = res if score_per_game is None else score_per_game + res



    pygame.quit()
    
    print(f"Score final de la partie = {score_per_game}")
    exit()


    #-----------------------------------------------------------

    # Les trois boucles servent au graphique
    fig, axes = plt.subplots(nrows=7, ncols=7, figsize=(14, 14), dpi=300, sharex=True, sharey=True)
    strategy_names = ["têtu", "stochastique", "coupe files", "greedy", "fictitious play", "greedy_min", "coupe files greedy min"]
    for nb_strat in range(7): # nombre de strategies
        for nb_strat2 in range(7): # Nombre de strategies aussi
            score_per_game_lst_0 = None
            score_per_game_lst_1_7 = None
            ax = axes[nb_strat, nb_strat2]
            nb_moyenne = 10
            for moyenne in range(nb_moyenne):
                score_per_game_lst_0_tmp = []
                score_per_game_lst_1_7_tmp = []


                nb_update = 25 # Nombre de maj au total pour regret et fictitious, >0, update une fois toutes les nb_days journees passees
                nb_days = 50 # Nombre de journees durant la partie
                assert nb_update <= nb_days and nb_days % nb_update == 0
                score_per_game = None

                for partie in range(nb_days):
                    if nb_days >= 100:
                        print(partie)
                    
                    init()

                    #-------------------------------
                    # Initialisation
                    #-------------------------------

                    nb_lignes = game.spriteBuilder.rowsize
                    nb_cols = game.spriteBuilder.colsize
                    assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
                    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker les objets)
                    lMax=nb_lignes-2
                    cMin=2
                    cMax=nb_cols-2

                    #-------------------------------
                    # Rapport de ce qui est trouve sut la carte
                    #-------------------------------
                    # print("lecture carte")
                    # print("-------------------------------------------")
                    # print('joueurs:', nb_players)
                    # print("restaurants:",nb_restos)
                    # print("lignes:", nb_lignes)
                    # print("colonnes:", nb_cols)
                    # print("coup_files:",nb_coupe_files)
                    # print(f"game.layers = {game.layers}")
                    # print("-------------------------------------------")

                    #-------------------------------
                    # Carte demo 
                    # 8 joueurs
                    # 5 restos
                    #-------------------------------

                    g = np.ones((nb_lignes, nb_cols), dtype=bool)  # une matrice remplie par defaut a True

                    for i in range(nb_lignes):  # on exclut aussi les bordures du plateau
                        g[0][i] = False
                        g[1][i] = False
                        g[nb_lignes - 1][i] = False
                        g[nb_lignes - 2][i] = False
                        g[i][0] = False
                        g[i][1] = False
                        g[i][nb_lignes - 1] = False
                        g[i][nb_lignes - 2] = False


                    players = [o for o in game.layers['joueur']]
                    nb_players = len(players)

                    pos_restaurants = [(3,4),(3,7),(3,10),(3,13),(3,16)] # 5 restaurants positionnes
                    nb_restos = len(pos_restaurants)
                    capacity = [1]*nb_restos # Capacite des restaurants fixe a 1

                    coupe_files = [o for o in game.layers["ramassable"]] # a utiliser dans le cas de la variante coupe-file
                    coupe_files_set = [] # Utile pour les strategies coupe_files 
                    nb_coupe_files= len(coupe_files)


                    joueurs = [Joueur(pla) for pla in players]

                    if nb_strat == 0: # Strategie tetu

                        joueurs[0].set_strat(Joueur.strat_tetu_stochastique) # On lui assigne une strategie
                        joueurs[0].set_choix_resto([4])

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([0])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([0])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([4])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    elif nb_strat == 1:

                        joueurs[0].set_strat(Joueur.strat_tetu_stochastique) # On lui assigne une strategie
                        joueurs[0].set_choix_resto([])

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([1])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([2])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([3])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    elif nb_strat == 2:

                        joueurs[0].set_strat(Joueur.strat_coupe_files) # On lui assigne une strategie
                        joueurs[0].set_choix_resto([])

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([2])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([2])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([2])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    elif nb_strat == 3:
                        r = [r for r in range(nb_restos)]
                        random.shuffle(r)

                        joueurs[0].set_strat(Joueur.strat_greedy) # On lui assigne une strategie
                        joueurs[0].set_choix_resto(r)

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([2])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([2])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([2])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    elif nb_strat == 4:

                        joueurs[0].set_strat(Joueur.strat_fictitious_play) # On lui assigne une strategie
                        joueurs[0].set_choix_resto([])

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([2])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([2])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([2])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    elif nb_strat == 5:
                        r = [r for r in range(nb_restos)]
                        random.shuffle(r)

                        joueurs[0].set_strat(Joueur.strat_greedy_min) # On lui assigne une strategie
                        joueurs[0].set_choix_resto(r)

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([2])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([2])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([2])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                    else:
                        r = [r for r in range(nb_restos)]
                        random.shuffle(r)

                        joueurs[0].set_strat(Joueur.strat_coupe_files_greedy_min) # On lui assigne une strategie
                        joueurs[0].set_choix_resto(r)

                        if nb_strat2 == 0: # Strategie tetu

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([0])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([0]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([0])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([0])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([4])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([4])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([4])

                        elif nb_strat2 == 1: # Strategie stochastique

                            joueurs[1].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_tetu_stochastique)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 2: # Strategie coupe files

                            joueurs[1].set_strat(Joueur.strat_coupe_files)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_coupe_files)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_coupe_files)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_coupe_files)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_coupe_files)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_coupe_files)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 3: # Strategie greedy
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        elif nb_strat2 == 4: # Strategy fictitious play

                            joueurs[1].set_strat(Joueur.strat_fictitious_play)
                            joueurs[1].set_choix_resto([])

                            joueurs[2].set_strat(Joueur.strat_fictitious_play)
                            joueurs[2].set_choix_resto([]) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_fictitious_play)
                            joueurs[3].set_choix_resto([])

                            joueurs[4].set_strat(Joueur.strat_fictitious_play)
                            joueurs[4].set_choix_resto([])

                            joueurs[5].set_strat(Joueur.strat_fictitious_play)
                            joueurs[5].set_choix_resto([])

                            joueurs[6].set_strat(Joueur.strat_fictitious_play)
                            joueurs[6].set_choix_resto([])

                            joueurs[7].set_strat(Joueur.strat_fictitious_play)
                            joueurs[7].set_choix_resto([])

                        elif nb_strat2 == 5: # Strategie greedy_min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)

                        else: # Strategie coupe files greedy min
                            r = [r for r in range(nb_restos)]

                            joueurs[1].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[1].set_choix_resto(r)

                            joueurs[2].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[2].set_choix_resto(r) # Car le choix du resto ne change pas entre chaque journee
                            
                            joueurs[3].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[3].set_choix_resto(r)

                            joueurs[4].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[4].set_choix_resto(r)

                            joueurs[5].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[5].set_choix_resto(r)

                            joueurs[6].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[6].set_choix_resto(r)

                            joueurs[7].set_strat(Joueur.strat_coupe_files_greedy_min)
                            random.shuffle(r)
                            joueurs[7].set_choix_resto(r)



                    # for j, joueur in enumerate(joueurs): # Pour afficher les etats de 
                    #     if joueur.strat == joueur.strat_fictitious_play:
                    #         print(Joueur.occupations_restos)

                    res = journee((partie + 1) % (nb_days // nb_update) == 0)
                    score_per_game = res if score_per_game is None else score_per_game + res

                    if (partie + 1) % (nb_days // nb_update) == 0: # Pour afficher le nombre exacte de MaJ
                        # print("Update !!!!!!")
                        score_per_game_lst_0_tmp.append(score_per_game[0])
                        score_per_game_lst_1_7_tmp.append(sum(score_per_game[1:]) / (len(score_per_game) - 1))


                pygame.quit()
                
                print(f"Score final de la partie = {score_per_game} et nb_strat = {nb_strat} et nb_strat2 = {nb_strat2} et moyenne = {moyenne}")
                
                score_per_game_lst_0 = np.array(score_per_game_lst_0_tmp) if score_per_game_lst_0 is None else score_per_game_lst_0 + np.array(score_per_game_lst_0_tmp)
                score_per_game_lst_1_7 = np.array(score_per_game_lst_1_7_tmp) if score_per_game_lst_1_7 is None else score_per_game_lst_1_7 + np.array(score_per_game_lst_1_7_tmp)
                

            score_per_game_lst_0 = (score_per_game_lst_0 / nb_moyenne).tolist()
            score_per_game_lst_1_7 = (score_per_game_lst_1_7 / nb_moyenne).tolist()
            score_per_game_nb_days = np.linspace(0, nb_days, nb_update, dtype = int).tolist()

            # Pour le graphique
            ax.plot(score_per_game_nb_days, score_per_game_lst_0, color = 'blue', lw = 1)
            ax.plot(score_per_game_nb_days, score_per_game_lst_1_7, color = 'red', lw = 1)
            # Optionnel : ajouter des ticks plus petits
            ax.tick_params(labelsize=8)

    # Ajout d'étiquettes en ordonnée sur la première colonne
    for i in range(7):
        axes[i, 0].set_ylabel(strategy_names[i], fontsize=6, rotation=0, labelpad=40, va='center')

    # Ajout d'étiquettes en dessous de chaque colonne
    # On utilise la position de la première ligne de chaque colonne pour placer le texte
    for j in range(7):
        pos = axes[6, j].get_position()  # Position de l'axe de la dernière ligne de la colonne j
        # pos.x0 est la position en x et pos.width la largeur de l'axe
        fig.text(pos.x0 + pos.width/2, pos.y0 - 0.02, strategy_names[j],
                ha='center', va='top', fontsize=6)

    # Ajout d'un titre global
    fig.suptitle("Affrontement des stratégies\nLignes : Stratégie du joueur solo | Colonnes : Stratégie des adversaires", fontsize=8)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

