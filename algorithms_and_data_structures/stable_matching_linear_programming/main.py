from typing import List, Dict, Tuple
import numpy as np
import random
import multiprocessing
import time
import math
import os

def lire_pref_etu(path: str) -> List[List[int]]:
    """
    Lit le fichier des préférences des étudiants et extrait les informations

    Returns:
        list: Une matrice des préférences des étudiants
    """
    file = open(path, "r")
    contenu = file.readlines()
    file.close()
    contenu.pop(0)

    for i in range(0, len(contenu)):
        contenu[i] = contenu[i].split()
        contenu[i].pop(0)
        contenu[i].pop(0)
        for j in range(len(contenu[i])):
            contenu[i][j] = int(contenu[i][j])
    return contenu


def lire_pref_parc(path: str) -> tuple[List[List[int]], List[int]]:
    """
    Lit le fichier des préférences des parcours et extrait les informations

    Returns:
        tuple: Une list/matrice des préférences et une liste des capacités des parcours
    """
    file = open(path, "r")
    contenu = file.readlines()
    file.close()
    contenu.pop(0)

    cap = contenu.pop(0).split()
    cap = cap[1:]
    cap = [int(cap[i]) for i in range(len(cap))]

    for i in range(0, len(contenu)):
        contenu[i] = contenu[i].split()
        contenu[i].pop(0)
        contenu[i].pop(0)
        for j in range(len(contenu[i])):
            contenu[i][j] = int(contenu[i][j])
    return contenu, cap


class Etu():

    def __init__(self, id, pref_etu_i, pref_parc):
        self.etu_id = id
        self.prop = 0
        self.is_free = True
        self.choosen_parc = 0
        self.pref_lst = pref_etu_i.copy()
        self.pref_lst.reverse()

        # liste des preferences
        # pour un etu h
        # pref[h] = classement de h
        self.pref_index_lst = list(range(len(pref_parc)))
        for i in range(len(pref_parc)):
            self.pref_index_lst[pref_etu_i[i]] = i

    def get_parc(self):
        return self.pref_lst.pop()
    
    def insert_parc(self, parc):
        self.choosen_parc = parc
        self.is_free = False


class Parc():

    def __init__(self, id, pref_etu, pref_parc_i, cap_i):
        self.parc_id = id
        self.choosen_etu_id = {} #init
        self.worst_etu = 0
        self.cap_max = cap_i
        self.is_free = True
        self.pref_lst = pref_parc_i.copy()
        self.pref_lst.reverse()

        # liste des preferences
        # pour un etu h
        # pref[h] = classement de h
        self.pref_index_lst = list(range(len(pref_etu)))
        for i in range(len(pref_etu)):
            self.pref_index_lst[pref_parc_i[i]] = i

    def insert_etu(self, etu):
        self.choosen_etu_id[self.pref_index_lst[etu.etu_id]] = etu
        self.update_worst_etu()
    
        if len(self.choosen_etu_id) == self.cap_max:
            self.is_free = False

    def switch_etu(self, etu, etu_prime):
        self.choosen_etu_id[self.pref_index_lst[etu.etu_id]] = etu
        self.remove_etu(etu_prime)

    def remove_etu(self, etu_prime):
        del self.choosen_etu_id[self.pref_index_lst[etu_prime.etu_id]]
        self.update_worst_etu()

    def remove_etu_hop(self, etu_prime):
        if self.pref_index_lst[etu_prime.etu_id] in self.choosen_etu_id.keys():
            del self.choosen_etu_id[self.pref_index_lst[etu_prime.etu_id]]
        self.update_worst_etu_hop()

    def update_worst_etu(self):
        worst_etu = -1 # valeur aberrante de classement
        for classement in self.choosen_etu_id.keys():
            if classement > worst_etu:
                worst_etu = classement
        self.worst_etu = self.choosen_etu_id[worst_etu] 

    def update_worst_etu_hop(self):
        worst_etu = -1 # valeur aberrante de classement
        for classement in self.choosen_etu_id.keys():
            if classement > worst_etu:
                worst_etu = classement
        if worst_etu != -1: 
            self.worst_etu = self.choosen_etu_id[worst_etu] 

    def get_etu(self):
        return self.pref_lst.pop()
    
    def update_parc(self, etu):
        """
        Sert a soit :
        - ajouter l'etudiant a ce parcours car la capacite max n'est pas encore atteinte
        - echanger un etudiant de parcours si il prefere celui ci a son ancien et on supprime \
        son ancienne affectation
        """
        if len(self.choosen_etu_id) < self.cap_max:
            self.insert_etu(etu)
        else:
            self.choosen_etu_id[self.pref_index_lst[etu.etu_id]] = etu
            if self.pref_index_lst[self.worst_etu.etu_id] in self.choosen_etu_id.keys():
                del self.choosen_etu_id[self.pref_index_lst[self.worst_etu.etu_id]]
            self.update_worst_etu_hop()

        

def gale_shapley_etu(Ce : List[List[int]], Cp : List[List[int]], cap : List[int], nb_iter : int = 0):
    # Pre-traitement
    parcs = [Parc(i, Ce, Cp[i], cap[i]) for i in range(len(Cp))]
    etus = [Etu(i, Ce[i], Cp) for i in range(len(Ce))]
    etus_libre = etus.copy()


    while etus_libre: # Tous les h libres
        etu = etus_libre.pop()
        parc = parcs[etu.get_parc()]

        if parc.is_free:
            # Si f est libre
            parc.insert_etu(etu)

        elif parc.pref_index_lst[etu.etu_id] < parc.pref_index_lst[parc.worst_etu.etu_id]:
            # Si f prefere h(etu) a son fiance h_prime(parc.worst_etu)
            etus_libre.append(parc.worst_etu) # h_prime libre
            parc.switch_etu(etu, parc.worst_etu) # f et h fiance

        else:
            # f rejette h
            etus_libre.append(etu)

        nb_iter += 1 # Compteur du nombre d'iterations


    # Post traitement
    res = {}
    for parc in parcs:
        res[parc.parc_id] = []
        for (etu_classement, etu) in parc.choosen_etu_id.items():
            # etu_classement = classement de l'etu pour le parcours ou il a ete affecte
            res[parc.parc_id].append(etu.etu_id)

    return res, nb_iter


def gale_shapley_parc(Ce : List[List[int]], Cp : List[List[int]], cap : List[int], nb_iter : int = 0):
    # Pre-traitement
    parcs = [Parc(i, Ce, Cp[i], cap[i]) for i in range(len(Cp))]
    etus = [Etu(i, Ce[i], Cp) for i in range(len(Ce))]
    parc_libre = parcs.copy()


    while parc_libre:
        parc = parc_libre.pop()
        etu = etus[parc.get_etu()]

        if etu.is_free:
            etu.insert_parc(parc)

            parc.update_parc(etu)
            if parc.is_free:
                parc_libre.append(parc)

        elif etu.pref_index_lst[parc.parc_id] < etu.pref_index_lst[etu.choosen_parc.parc_id]:

            parcs[etu.choosen_parc.parc_id].remove_etu_hop(etu) # On retire l'etudiant de son ancien parcours
            parc_libre.append(etu.choosen_parc) # On ajoute son ancien parcours aux parcours libre car 1 place se libere
            etu.insert_parc(parc)

            parc.update_parc(etu)
            if parc.is_free:
                parc_libre.append(parc)

        else:
            parc_libre.append(parc)

        nb_iter += 1 # Compteur du nombre d'iterations


    # Post traitement
    res = {}
    for parc in parcs:
        res[parc.parc_id] = []
        for (etu_classement, etu) in parc.choosen_etu_id.items():
            # etu_classement = classement de l'etu pour le parcours ou il a ete affecte
            res[parc.parc_id].append(etu.etu_id)

    return res, nb_iter


def paires_instables(res: Dict[int, List[int]], Ce: List[List[int]], Cp: List[List[int]]) -> List[Tuple[int, int]]:
    """
    Identifie toutes les paires instables selon les préférences

    Returns:
        List[Tuple[int, int]]: Liste des paires instables (étudiant, parc)
    """
    # 1. Précalculer la position des étudiants/parcs dans les préférences pour des accès O(1)
    student_rank_in_parc = [{} for _ in Cp]  # student_rank_in_parc[p][e] = rang de e dans Cp[p]
    for p in range(len(Cp)):
        for idx, e in enumerate(Cp[p]):
            student_rank_in_parc[p][e] = idx

    parc_rank_in_student = [{} for _ in Ce]  # parc_rank_in_student[e][p] = rang de p dans Ce[e]
    for e in range(len(Ce)):
        for idx, p in enumerate(Ce[e]):
            parc_rank_in_student[e][p] = idx

    # 2. Créer un dictionnaire étudiant -> parc actuel
    current_parc_for_student = {}
    for p in res:
        for e in res[p]:
            current_parc_for_student[e] = p

    # 3. Chercher les paires instables
    unstable_pairs = set()  # Éviter les doublons avec un set

    for p in res:
        for e in res[p]:
            # Tous les étudiants que p préfère à e (ceux avant e dans Cp[p])
            preferred_students = Cp[p][:student_rank_in_parc[p][e]]

            for pref_e in preferred_students:
                current_p = current_parc_for_student.get(pref_e, -1)
                if current_p == -1:
                    continue  # Étudiant non assigné (cas impossible si matching complet)

                # Vérifier si pref_e préfère p à son parc actuel
                if parc_rank_in_student[pref_e][p] < parc_rank_in_student[pref_e][current_p]:
                    unstable_pairs.add((pref_e, p))

    return list(unstable_pairs)


def generate_Ce(n : int) -> List[List[int]]:
    """
    Renvoit une matrice de preferences de 9 parcours aleatoirement
    Params
    -------
        n : int
        Nombre d'etudiants
    Returns
    -------
        List[List[int]]
        Matrice de preferences parmi 9 parcours de n etudiants
    """
    return [random.sample(range(9), 9) for i in range(n)]

def generate_Cp(n : int) -> List[List[int]]:
    """
    Renvoit une matrice de preferences de n etudiants aleatoirement
    Params
    -------
        n : int
        Nombre d'etudiants
    Returns
    -------
        List[List[int]]
        Matrice de preferences parmi n etudiant de 9 parcours
    """
    return [random.sample(range(n), n) for i in range(9)]


def generate_cap(n : int) -> List[int]:
    """
    Renvoit une liste de capacite reparties uniformement telle que sum(cap) = n
    Params
    ------
        n : int
        Nombre d'etudiants
    Returns
    ------
        List[int]
        Liste des capacites pour chaque parcours
    """
    cap = [int(n/9) for _ in range(9)]     # Generation des parametres
    while sum(cap) < n:                    # pour les algos cote etu et
        cap[random.randint(0, 8)] += 1     # cote parcours
    return cap


def compute_time(cote, n, n_moy):
    """
    Renvoit le temps d'execution reel et le nombre d'iteration reel en moyenne (n_moy)
    Params
    -----
        cote = fonction que l'on va appeler (gale_shapley{etu, parc})
        n : int = nombre d'etudiant
        n_moy : int = nombre d'iteration par n pour le calcul de moyenne
    Returns
    -------
        tuple : (temps d'execution reel en moyenne, nombre d'iteration reel en moyenne)
    """
    temps = 0
    iters = 0
    for moy in range(n_moy):

        Ce = generate_Ce(n)
        Cp = generate_Cp(n)
        cap = generate_cap(n)
        t1 = time.time()
        GS, TPS = cote(Ce, Cp, cap)
        t2 = time.time() - t1

        assert paires_instables(GS, Ce, Cp) == [] # On verifie a chaque iteration
                                                 # que le resultat est bien valide
        temps += t2
        iters += TPS
    return temps / n_moy, iters / n_moy


def theory_compute_time(n, complexity, n_moy):
    """
    Renvoit le temps d'execution theorique et le nombre d'iteration theorique en moyenne (n_moy)
    Params
    -----
        n : int = nombre d'etudiant
        complexity : int = complexite que l'on veut tester
        n_moy : int = nombre d'iteration par n pour le calcul de moyenne
    Returns
    -------
        tuple : (temps d'execution theorique en moyenne, nombre d'iteration theorique en moyenne)
    """
    temps = 0
    iters = 0
    for moy in range(n_moy):

        t1 = time()
        for i in range(n): # boucle while de l'algo en lui meme
            for j in range(complexity): # complexite a l'interieur du while
                1 + 1
        t2 = time() - t1

        temps += t2
        iters += n * complexity
    return temps / n_moy, iters / n_moy


def compute_time_GS_moy(cote, dat_file):
    """
    Calcul le temps d'execution et le nombre d'iteration moyen pour differentes valeurs de n
    et sauvegarde les resultats dans le fichier dat_file
    Params
    ------
        cote = gale_shapley{etu, parc} la fonction que l'on va appeler
        dat_file : str = nom du fichier dans lequel les resultats seront sauvegardes
    """

    n_processes = multiprocessing.cpu_count()
    write_comput_time = ""

    for n in range(200, 2001, 100):

        write_comput_time += f"{n} " # 1ere colonne du fichier dat
        write_iters = ""
        n_moy = 300 # n_moy * n_processes iterations par n pour le calcul de moyenne (>10)
        
        # Calcule des temps d'executions reels
        with multiprocessing.Pool(processes = n_processes) as pool:
            params_per_process = [(cote, n, n_moy) for _ in range(n_processes)]
            temps_moy = pool.starmap(compute_time, params_per_process) # plusieurs tests

        temps_moy_0 = np.array(temps_moy)               #
        temps_moy = float(np.mean(temps_moy_0[:, 0]))   #
        iters = float(np.mean(temps_moy_0[:, 1]))       # Sauvegarde des temps
                                                        # d'execution et du
        write_comput_time += str(temps_moy) + " "       # nombre d'iterations
        write_iters += f"{iters} "                      # pour le fichier dat
        print(f"n = {n}; temps_moy = {temps_moy}")      #

        # Calcule des temps d'executions theoriques
        for thoery_complexity in [1, int(math.log(n, 2)), max(generate_cap(n)), n]:
            with multiprocessing.Pool(processes = n_processes) as pool:
                params_per_process = [(n, thoery_complexity, n_moy) for _ in range(n_processes)]
                temps_moy = pool.starmap(theory_compute_time, params_per_process) # plusieurs tests

            temps_moy_0 = np.array(temps_moy)                                   #
            temps_moy = float(np.mean(temps_moy_0[:, 0]))                       # Sauvegarde des temps
            iters = float(np.mean(temps_moy_0[:, 1]))                           # d'execution et du 
                                                                                # nombre d'iterations
            write_comput_time += str(temps_moy) + " "                           # pour le fichier dat
            write_iters += f"{iters} "                                          #
            print(f"Complexity = {thoery_complexity} : time = {temps_moy}")     #

        write_comput_time += f"{write_iters}\n" # retour a la ligne a la fin de la valeur n

    # Ecriture dans les fichiers dat des temps calcules
    file = open(dat_file + ".dat", "w")
    file.write(write_comput_time)
    file.close()


def main():

    Ce = lire_pref_etu("data/PrefEtu.txt")
    Cp, cap = lire_pref_parc("data/PrefSpe.txt")
    print(gale_shapley_etu(Ce, Cp, cap)[0])
    print(gale_shapley_parc(Ce, Cp, cap)[0])

    # functions = [gale_shapley_etu, gale_shapley_parc]
    # dat_functions = ["Cote_etu", "Cote_parcours"]

    #for (fun, dat_fun) in zip(functions, dat_functions):
    #    # Attention a bien changer la valeur de n_moy pour ne pas prendre trop de temps de calcul
    #    compute_time_GS_moy(fun, dat_fun)
    #    os.system(f"gnuplot {dat_fun}_tps.gp")
    #    os.system(f"gnuplot {dat_fun}_ite.gp")


if __name__ == '__main__':
    main()
