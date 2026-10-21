import pandas as pd
import numpy as np
from utils import *
import math
from scipy.stats import chi2_contingency

def getPrior(df):
    """
    Calcule les probabilités a priori pour la classe cible (target) dans un DataFrame.

    Cette fonction calcule la probabilité d'appartenance à la classe 1 (p) et les intervalles de confiance 
    à 95% pour cette probabilité (min5pourcent et max5pourcent).

    Args:
        df (DataFrame): Le DataFrame contenant les données, avec une colonne 'target'.

    Returns:
        dict: Un dictionnaire contenant la probabilité a priori de la classe 1 ('estimation'), 
              ainsi que les bornes inférieure et supérieure de l'intervalle de confiance à 95% ('min5pourcent', 'max5pourcent').
    """
    n = len(df)
    
    count_class_1 = df['target'].sum()
    
    p = count_class_1 / n
    
    margin = 1.96 * np.sqrt(p * (1 - p) / n)
    min_ci = p - margin
    max_ci = p + margin
    
    return {
        'estimation': p,
        'min5pourcent': min_ci,
        'max5pourcent': max_ci
    }

class APrioriClassifier(AbstractClassifier):
    """
    Classe de classifieur a priori qui estime la classe majoritaire en se basant uniquement sur la probabilité a priori.

    Cette classe suppose que la classe majoritaire (la classe ayant la probabilité a priori la plus élevée) est la prédiction.

    Args:
        train_df (DataFrame): Le DataFrame d'apprentissage utilisé pour estimer les probabilités a priori.
    """
    def __init__(self, train_df):
        super().__init__()
        self.train_df = train_df
        prior = getPrior(train_df)
        self.prior_prob = prior['estimation']
        self.majority_class = 1 if self.prior_prob > 0.5 else 0
        
    def estimClass(self, attrs):
        """
        Estime la classe d'un individu en fonction de la classe majoritaire.

        Args:
            attrs (dict): Un dictionnaire représentant un individu avec ses attributs.

        Returns:
            int: La classe estimée (0 ou 1).
        """
        return self.majority_class

    def statsOnDF(self, df):
        """
        Calcule les statistiques de performance (VP, VN, FP, FN, Précision, Rappel) sur un DataFrame donné.

        Args:
            df (DataFrame): Le DataFrame contenant les données et les véritables classes.

        Returns:
            dict: Un dictionnaire contenant les statistiques de performance : VP, VN, FP, FN, Précision, Rappel.
        """
        VP = VN = FP = FN = 0

        for i in range(len(df)):
            dic = getNthDict(df, i)
            predicted_class = self.estimClass(dic)
            actual_class = dic['target']
            
            if predicted_class == 1 and actual_class == 1:
                VP += 1
            elif predicted_class == 0 and actual_class == 0:
                VN += 1
            elif predicted_class == 1 and actual_class == 0:
                FP += 1
            elif predicted_class == 0 and actual_class == 1:
                FN += 1
        
        precision = VP / (VP + FP) if (VP + FP) > 0 else 0
        recall = VP / (VP + FN) if (VP + FN) > 0 else 0

        return {
            'VP': VP,
            'VN': VN,
            'FP': FP,
            'FN': FN,
            'Précision': precision,
            'Rappel': recall
        }

def P2D_l(df, attr):
    """
    Calcule les probabilités conditionnelles P(attr=a | target=t) pour un attribut donné.

    Cette fonction calcule la probabilité conditionnelle de l'attribut `attr` pour chaque valeur de la cible `target`.

    Args:
        df (DataFrame): Le DataFrame contenant les données.
        attr (str): Le nom de l'attribut dont les probabilités conditionnelles doivent être calculées.

    Returns:
        dict: Un dictionnaire contenant les probabilités conditionnelles P(attr=a | target=t).
    """
    prob = {}
    
    target_values = df['target'].unique()
    attr_values = df[attr].unique()
    
    for t in target_values:
        prob[t] = {}
        target_t_df = df[df['target'] == t]
        total_t = len(target_t_df)
        
        for a in attr_values:
            count_a_given_t = len(target_t_df[target_t_df[attr] == a])
            prob[t][a] = count_a_given_t / total_t
    
    return prob

def P2D_p(df, attr):
    """
    Calcule les probabilités conditionnelles P(target=t | attr=a) pour un attribut donné.

    Cette fonction calcule la probabilité conditionnelle de la cible `target` pour chaque valeur de l'attribut `attr`.

    Args:
        df (DataFrame): Le DataFrame contenant les données.
        attr (str): Le nom de l'attribut dont les probabilités conditionnelles doivent être calculées.

    Returns:
        dict: Un dictionnaire contenant les probabilités conditionnelles P(target=t | attr=a).
    """
    prob = {}
    
    target_values = df['target'].unique()
    attr_values = df[attr].unique()
    
    for a in attr_values:
        prob[a] = {}
        attr_a_df = df[df[attr] == a]
        total_a = len(attr_a_df)
        
        for t in target_values:
            count_t_given_a = len(attr_a_df[attr_a_df['target'] == t])
            prob[a][t] = count_t_given_a / total_a
    
    return prob

class ML2DClassifier(APrioriClassifier):
    """
    Classifieur basé sur la méthode du maximum a posteriori pour un attribut spécifique.

    Cette classe utilise les probabilités conditionnelles P(attr=a | target=t) pour estimer la classe 
    d'un individu en utilisant la règle de Bayes.

    Args:
        train_df (DataFrame): Le DataFrame d'apprentissage utilisé pour calculer les probabilités.
        attr (str): Le nom de l'attribut utilisé pour effectuer la classification.
    """
    def __init__(self, train_df, attr):
        super().__init__(train_df)
        self.attr = attr
        self.p2d_l = P2D_l(train_df, attr)
        self.prior = getPrior(train_df)
        self.p_attr = train_df[attr].value_counts(normalize=True).to_dict()

    def estimClass(self, attrs):
        attr_value = attrs[self.attr]
    
        p_attr_given_target = {t: self.p2d_l[t].get(attr_value, 0) for t in [0, 1]}
    
        p_target_0_given_attr = p_attr_given_target[0]
        p_target_1_given_attr = p_attr_given_target[1]

        if p_target_0_given_attr > p_target_1_given_attr:
            return 0
        elif p_target_1_given_attr > p_target_0_given_attr:
            return 1
        else:
            return 0

    def statsOnDF(self, df):
        return super().statsOnDF(df)

class MAP2DClassifier(APrioriClassifier):
    """
    Classifieur basé sur la méthode du maximum a posteriori pour un attribut spécifique.

    Cette classe utilise les probabilités conditionnelles P(target=t | attr=a) pour estimer la classe 
    d'un individu en utilisant la règle de Bayes avec les probabilités calculées par la fonction P2D_p.

    Args:
        train_df (DataFrame): Le DataFrame d'apprentissage utilisé pour calculer les probabilités.
        attr (str): Le nom de l'attribut utilisé pour effectuer la classification.
    """
    def __init__(self, train_df, attr):
        super().__init__(train_df)
        self.attr = attr
        self.p2d_p = P2D_p(train_df, attr)  # Utilise les probabilités calculées
        self.prior = getPrior(train_df)
        self.p_attr = train_df[attr].value_counts(normalize=True).to_dict()
        
    def estimClass(self, attrs):
        """
        Estime la classe de l'individu en utilisant la règle du maximum a posteriori (MAP).

        Args:
            attrs (dict): Un dictionnaire représentant un individu avec ses attributs.

        Returns:
            int: La classe estimée (0 ou 1).
        """
        attr_value = attrs[self.attr]
        
        p_target_given_attr = {t: self.p2d_p.get(attr_value, {}).get(t, 0) for t in [0, 1]}

        p_target_0_given_attr = p_target_given_attr[0]
        p_target_1_given_attr = p_target_given_attr[1]
        
        if p_target_0_given_attr > p_target_1_given_attr:
            return 0
        elif p_target_1_given_attr > p_target_0_given_attr:
            return 1
        else:
            return 0

    def statsOnDF(self, df):
        return super().statsOnDF(df)


def nbParams(df, attrs=None):
    """
    Calcule la taille mémoire nécessaire pour représenter la table de probabilités
    d'un DataFrame donné en supposant que chaque valeur est représentée par un float 
    (8 octets), et que la taille de la table est déterminée par le produit des tailles 
    des attributs.

    Paramètres:
        - df : DataFrame contenant les variables dont on veut calculer la taille mémoire.
    - attrs : Liste des colonnes (attributs) du DataFrame pour lesquelles on souhaite
      calculer la taille mémoire. Si None, toutes les colonnes du DataFrame sont utilisées.

    Retourne:
        - La taille mémoire totale en octets pour représenter la table de probabilités.
    Affiche également la taille mémoire dans différentes unités (octets, Ko, Mo, Go, To).
    """
    if attrs is None:
        attrs = [col for col in df.columns]

    # Taille de chaque attribut (nombre de valeurs uniques)
    attr_sizes = [len(df[attr].unique()) for attr in attrs]

    # Calcul de la taille de la table (produit des tailles des attributs)
    table_size = math.prod(attr_sizes)

    # Taille mémoire totale (en octets, avec 8 octets par valeur)
    memory_size = table_size * 8

    # Affichage de la taille mémoire en fonction de l'unité
    if memory_size < 1024:
        print(f"{len(attrs)} variable(s) : {memory_size} octets")
    elif memory_size < 1024**2:
        ko = memory_size // 1024
        o = memory_size % 1024
        print(f"{len(attrs)} variable(s) : {memory_size} octets = {ko}ko {o}o")
    elif memory_size < 1024**3:
        mo = memory_size // 1024**2
        ko = (memory_size % 1024**2) // 1024
        print(f"{len(attrs)} variable(s) : {memory_size} octets = {mo}mo {ko}ko {memory_size % 1024}o")
    elif memory_size < 1024**4:
        go = memory_size // 1024**3
        mo = (memory_size % 1024**3) // 1024**2
        ko = (memory_size % 1024**2) // 1024
        print(f"{len(attrs)} variable(s) : {memory_size} octets = {go}go {mo}mo {ko}ko {memory_size % 1024}o")
    else:
        to = memory_size // 1024**4
        print(f"{len(attrs)} variable(s) : {memory_size} octets = {to}to")

    return memory_size

def nbParamsIndep(df, attrs=None):
    """
    Calcule la taille mémoire nécessaire pour représenter les tables de probabilités
    en supposant l'indépendance des variables. Chaque variable est représentée par un
    nombre de valeurs uniques multiplié par 8 octets (taille d'un float).

    Paramètres:
        - df : DataFrame contenant les variables dont on veut calculer la taille mémoire.
    - attrs : Liste des colonnes (attributs) du DataFrame pour lesquelles on souhaite
      calculer la taille mémoire sous l'hypothèse d'indépendance. Si None, toutes les colonnes
      du DataFrame sont utilisées.

    Retourne:
        - La taille mémoire totale en octets sous l'hypothèse d'indépendance.
    Affiche également la taille mémoire totale en octets.
    """
    if attrs is None:
        attrs = [col for col in df.columns]

    total_memory = 0
    for attr in attrs:
        # Calcul du nombre de valeurs uniques par attribut
        num_unique_values = len(df[attr].unique())

        # Calcul de la mémoire pour cet attribut (8 octets par valeur)
        memory_for_attr = num_unique_values * 8
        total_memory += memory_for_attr

    # Affichage de la taille mémoire totale
    print(f"{len(attrs)} variable(s) : {total_memory} octets")
    return total_memory

def drawNaiveBayes(df, target):
    arcs = ";".join([f"{target}->{col}" for col in df.columns if col != target])
    return drawGraph(arcs)

def nbParamsNaiveBayes(df, target, attrs=None):
    if attrs is None:
        attrs = [col for col in df.columns if col != target]

    if len(attrs) == 0:
        target_memory = len(df[target].unique()) * 8
        print(f"0 variable(s) : {target_memory} octets")
        return target_memory

    attrs = [attr for attr in attrs if attr != target]

    # Taille mémoire pour la distribution de target
    target_memory = len(df[target].unique()) * 8

    # Taille mémoire pour les distributions conditionnelles de chaque attribut
    conditional_memory = sum(len(df[target].unique()) * len(df[attr].unique()) * 8 for attr in attrs)

    # Total mémoire
    total_memory = target_memory + conditional_memory

    # Affichage du résultat
    if total_memory < 1024:
        print(f"{len(attrs)+1} variable(s) : {total_memory} octets")
    elif total_memory < 1024**2:
        ko = total_memory // 1024
        o = total_memory % 1024
        print(f"{len(attrs)+1} variable(s) : {total_memory} octets = {ko}ko {o}o")
    elif total_memory < 1024**3:
        mo = total_memory // 1024**2
        ko = (total_memory % 1024**2) // 1024
        print(f"{len(attrs)+1} variable(s) : {total_memory} octets = {mo}mo {ko}ko {total_memory % 1024}o")
    else:
        go = total_memory // 1024**3
        mo = (total_memory % 1024**3) // 1024**2
        print(f"{len(attrs)+1} variable(s) : {total_memory} octets = {go}go {mo}mo")

    return total_memory

class MLNaiveBayesClassifier(APrioriClassifier):
    def __init__(self, train_df):
        super().__init__(train_df)
        self.attributes = [col for col in train_df.columns if col != "target"]
        self.p2d_l = {attr: P2D_l(train_df, attr) for attr in self.attributes}
        self.prior = getPrior(train_df)
        self.p_attr = {attr: train_df[attr].value_counts(normalize=True).to_dict()
                       for attr in self.attributes}

    def estimProbas(self, attrs):
        prob_0 = 1
        prob_1 = 1

        for attr, value in attrs.items():
            if attr in self.p2d_l:
                prob_0 *= self.p2d_l[attr][0].get(value, self.p_attr[attr].get(value, 0))
                prob_1 *= self.p2d_l[attr][1].get(value, self.p_attr[attr].get(value, 0))

        return {0: prob_0, 1: prob_1}

    def estimClass(self, attrs):
        probas = self.estimProbas(attrs)
        return 1 if probas[1] > probas[0] else 0

    def statsOnDF(self, df):
        return super().statsOnDF(df)

class MAPNaiveBayesClassifier(APrioriClassifier):
    """
    Classifieur naïve bayes basé sur le maximum a posteriori (MAP).
    Cette classe suppose que les attributs sont conditionnellement indépendants
    les uns des autres étant donné la variable cible (target).
    """

    def __init__(self, train_df):
        super().__init__(train_df)
        self.attributes = [col for col in train_df.columns if col != "target"]

        # Calculer les probabilités conditionnelles P(attr=a | target=t) pour chaque attribut
        self.p2d_l = {attr: P2D_l(train_df, attr) for attr in self.attributes}

        # Calculer les probabilités a priori de target
        self.prior = getPrior(train_df)

        # Calculer les probabilités marginales P(attr) pour chaque attribut
        self.p_attr = {attr: train_df[attr].value_counts(normalize=True).to_dict() for attr in self.attributes}

    def estimProbas(self, attrs):
        """
        Estime les probabilités a posteriori P(target | attr1, attr2, ...) 
        en utilisant le maximum a posteriori (MAP).

        Args:
            attrs (dict): Un dictionnaire représentant un individu avec ses attributs.

        Returns:
            dict: Un dictionnaire contenant les probabilités {0: prob0, 1: prob1}.
        """
        # Initialiser les probabilités avec les priors P(target)
        prob_0 = 1 - self.prior["estimation"]  # P(target=0)
        prob_1 = self.prior["estimation"]  # P(target=1)

        # Calculer la probabilité de chaque attribut P(attr) et les probabilités conditionnelles P(attr|target)
        prob_attr_0 = 1
        prob_attr_1 = 1

        for attr, value in attrs.items():
            if attr in self.p2d_l:
                # Calculer P(attr|target=0) et P(attr|target=1)
                prob_attr_0 *= self.p2d_l[attr].get(0, {}).get(value, 0)
                prob_attr_1 *= self.p2d_l[attr].get(1, {}).get(value, 0)

        # Calculer la normalisation pour P(attr1)*P(attr2)*...
        normalisation = 1
        for attr in attrs:
            if attr in self.p_attr:
                normalisation *= self.p_attr[attr].get(attrs[attr], 1)  # P(attr) pour chaque attribut

        # Calculer les probabilités a posteriori en utilisant la formule MAP
        prob_0 = prob_0 * prob_attr_0 / normalisation
        prob_1 = prob_1 * prob_attr_1 / normalisation

        # Normaliser les probabilités
        total_prob = prob_0 + prob_1
        if total_prob == 0:
            return {0: 0.5, 1: 0.5}  # Cas où les probabilités sont égales (cas pathologique)

        return {0: prob_0 / total_prob, 1: prob_1 / total_prob}

    def estimClass(self, attrs):
        """
        Estime la classe en utilisant les probabilités calculées par estimProbas.

        Args:
            attrs (dict): Un dictionnaire représentant un individu avec ses attributs.

        Returns:
            int: La classe estimée (0 ou 1).
        """
        probas = self.estimProbas(attrs)
        return 1 if probas[1] > probas[0] else 0

    def statsOnDF(self, df):
        return super().statsOnDF(df)

def isIndepFromTarget(df, attr, x):
    contingency_table = pd.crosstab(df[attr], df['target'])
    chi2, p, _, _ = chi2_contingency(contingency_table)
    return p >= x

class ReducedMLNaiveBayesClassifier(MLNaiveBayesClassifier):
    def __init__(self, train_df, significance_level):
        self.selected_attributes = [
                attr for attr in train_df.columns if attr != "target" and not isIndepFromTarget(train_df, attr, significance_level)
                ]
        reduced_train_df = train_df[self.selected_attributes + ["target"]]
        super().__init__(reduced_train_df)
    def draw(self):
        reduced_df = self.train_df[self.selected_attributes]
        return drawNaiveBayes(reduced_df, "target")

class ReducedMAPNaiveBayesClassifier(MAPNaiveBayesClassifier):
    def __init__(self, train_df, significance_level):
        self.selected_attributes = [
                attr for attr in train_df.columns if attr != "target" and not isIndepFromTarget(train_df, attr, significance_level)
                ]
        reduced_train_df = train_df[self.selected_attributes + ["target"]]
        super().__init__(reduced_train_df)

    def draw(self):
        reduced_df = self.train_df[self.selected_attributes]
        return drawNaiveBayes(reduced_df, "target")

def mapClassifiers(dic, df):
    """
    Représente graphiquement les classifiers dans l'espace précision-rappel avec des limites [0,1] et des 'x' comme marqueurs.

    Args:
        dic (dict): Dictionnaire contenant {nom: instance du classifier}.
        df (DataFrame): DataFrame contenant les données à évaluer.
    """
    plt.figure(figsize=(8, 6))
    plt.xlabel("Précision")
    plt.ylabel("Rappel")
    plt.title("Précision vs Rappel des Classifieurs")

    for name, classifier in dic.items():
        # Statistiques sur le DataFrame
        stats = classifier.statsOnDF(df)
        precision = stats['Précision']
        rappel = stats['Rappel']

        # Afficher chaque point avec un 'x'
        plt.scatter(precision, rappel, label=name, color='red', marker='x')
        plt.text(precision, rappel, name, fontsize=10)

    # Ajouter une ligne guide au point idéal
    plt.axvline(x=1, color='grey', linestyle='--', linewidth=0.5)
    plt.axhline(y=1, color='grey', linestyle='--', linewidth=0.5)
    plt.grid()
    plt.legend()
    plt.show()

### 7.1
def MutualInformation(df, target, attr):
    """
    Calcule l'information mutuelle entre une variable cible (target) et un attribut (attr).

    Paramètres
    ----------
    df : pandas.DataFrame
        Le DataFrame contenant les données.
    target : str
        Le nom de la colonne représentant la variable cible.
    attr : str
        Le nom de la colonne représentant l'attribut.

    Retourne
    -------
    float
        La valeur de l'information mutuelle entre la cible et l'attribut.
    """
    joint_prob = pd.crosstab(df[attr], df[target], normalize=True)
    p_x = joint_prob.sum(axis=1)
    p_y = joint_prob.sum(axis=0)
    mi = 0.0
    for x in p_x.index:
        for y in p_y.index:
            p_xy = joint_prob.at[x, y]
            if p_xy > 0:  # Avoid log(0)
                mi += p_xy * np.log2(p_xy / (p_x[x] * p_y[y]))

    return mi


def ConditionalMutualInformation(df, attr1, attr2, target):
    """
    Calcule l'information mutuelle conditionnelle entre deux attributs, 
    étant donné la variable cible (target).

    Paramètres
    ----------
    df : pandas.DataFrame
        Le DataFrame contenant les données.
    attr1 : str
        Le nom de la première colonne représentant un attribut.
    attr2 : str
        Le nom de la deuxième colonne représentant un attribut.
    target : str
        Le nom de la colonne représentant la variable cible.

    Retourne
    -------
    float
        La valeur de l'information mutuelle conditionnelle.
    """


    # Calculer les probabilités jointes P(x, y, z)
    joint_prob_xyz = pd.crosstab([df[attr1], df[attr2]], df[target], normalize=True).stack()

    # Calculer les probabilités marginales P(x, z) et P(y, z)
    joint_prob_xz = pd.crosstab(df[attr1], df[target], normalize=True).stack()
    joint_prob_yz = pd.crosstab(df[attr2], df[target], normalize=True).stack()

    # Calculer les probabilités marginales P(x, z) et P(y, z)
    prob_z = df[target].value_counts(normalize=True)

    conditional_mi = 0.0
    for (x, y, z), p_xyz in joint_prob_xyz.items():
        p_xz = joint_prob_xz.get((x, z), 0)
        p_yz = joint_prob_yz.get((y, z), 0)
        p_z = prob_z.get(z, 0)

        # Éviter log(0) en vérifiant que toutes les probabilités sont positives
        if p_xyz > 0 and p_xz > 0 and p_yz > 0 and p_z > 0:
            conditional_mi += p_xyz * np.log2((p_z * p_xyz) / (p_xz * p_yz))

    return conditional_mi


### 7.2
def MeanForSymetricWeights(cmis):
    """
    Calcule la moyenne des poids symétriques dans une matrice d'informations mutuelles conditionnelles.

    Paramètres
    ----------
    cmis : numpy.ndarray
        Une matrice carrée contenant les informations mutuelles conditionnelles entre attributs.

    Retourne
    -------
    float
        La moyenne des poids symétriques dans la matrice.
    """

    longueur = len(cmis)
    sum = 0
    for i in range(longueur):
        for j in range(i):
            sum += cmis[i][j]

    return sum / (longueur*(longueur-1)/2)

def SimplifyConditionalMutualInformationMatrix(cmis):
    """
    Simplifie une matrice d'informations mutuelles conditionnelles en supprimant les poids faibles.
    En mettant à zéro les valeurs inférieures à la moyenne des poids symétriques dans la matrice.

    Paramètres
    ----------
    cmis : numpy.ndarray
        Une matrice carrée contenant les informations mutuelles conditionnelles entre attributs.

    Retourne
    -------
    None
        Modifie directement la matrice passée en paramètre.
    """
    moy = MeanForSymetricWeights(cmis)
    longueur = len(cmis)
    for i in range(longueur):
        for j in range(longueur):
            if cmis[i][j] < moy:
                cmis[i][j] = 0


### 7.3
def find(parent, i):
    """
    Trouve le représentant (racine) d'un élément dans un ensemble disjoint.

    Paramètres
    ----------
    parent : dict
        Un dictionnaire où chaque clé est un élément et la valeur est son parent.
    i : Any
        L'élément pour lequel on souhaite trouver le représentant.

    Retourne
    -------
    Any
        Le représentant (racine) de l'ensemble contenant l'élément i.
    """
    if parent[i] != i:
        parent[i] = find(parent, parent[i])
    return parent[i]


def union(parent, rank, x, y):
    """
    Fusionne deux ensembles disjoints représentés par leurs racines.

    Paramètres
    ----------
    parent : dict
        Un dictionnaire où chaque clé est un élément et la valeur est son parent.
    rank : dict
        Un dictionnaire où chaque clé est un élément et la valeur est son rang 
        (profondeur approximative de l'arbre).
    x : Any
        La racine du premier ensemble.
    y : Any
        La racine du second ensemble.

    Retourne
    -------
    None
        Modifie directement les dictionnaires `parent` et `rank`.
    """

    root_x = find(parent, x)
    root_y = find(parent, y)

    if rank[root_x] < rank[root_y]:
        parent[root_x] = root_y
    elif rank[root_x] > rank[root_y]:
        parent[root_y] = root_x
    else:
        parent[root_y] = root_x
        rank[root_x] += 1


def Kruskal(df, cmis):
    """
    Applique l'algorithme de Kruskal pour construire un arbre couvrant minimal à partir 
    d'une matrice d'informations mutuelles conditionnelles.

    Paramètres
    ----------
    df : pandas.DataFrame
        Le DataFrame contenant les colonnes représentant les attributs.
    cmis : numpy.ndarray
        Une matrice carrée contenant les informations mutuelles conditionnelles entre attributs.

    Retourne
    -------
    list
        Une liste de tuples représentant les arcs de l'arbre couvrant minimal, 
        sous la forme (attribut1, attribut2, poids).
    """
    longueur = len(cmis)
    arcs = []
    # Créer une liste des arcs avec leur poids
    for i in range(longueur):
        for j in range(i):
            if cmis[i][j] != 0:
                temp_tup = (df.keys()[j], df.keys()[i], cmis[i][j])
                arcs.append(temp_tup)

    # Trier les arcs par poids en ordre décroissant
    arcs = sorted(arcs, key=lambda item: item[2], reverse=True)

    parent = {}
    rank = {}

    # Initialiser les ensembles disjoints pour chaque sommet
    for vertex in df.keys():
        parent[vertex] = vertex
        rank[vertex] = 0

    mst = []

    # Appliquer l'algorithme de Kruskal pour construire l'arbre couvrant minimal
    for arc in arcs:
        u, v, _ = arc
        if find(parent, u) != find(parent, v):
            union(parent, rank, u, v)
            mst.append(arc)

    return mst


def ConnexSets(list_arcs):
    """
    Calcule les ensembles connexes d'un graphe représenté par une liste d'arcs.

    Paramètres
    ----------
    list_arcs : list of tuple
        Une liste d'arcs, où chaque arc est représenté par un tuple (noeud1, noeud2).

    Retourne
    -------
    list of set
        Une liste d'ensembles, où chaque ensemble contient les nœuds appartenant à une composante connexe.
    """
    liste_ensembles = []
    for arc in list_arcs:
        added = 0
        for ensemble in liste_ensembles:
            if arc[0] in ensemble or arc[1] in ensemble:
                ensemble.add(arc[0])
                ensemble.add(arc[1])
                added = 1
                break
        if added == 0:
            liste_ensembles.append({arc[0], arc[1]})

    return liste_ensembles



def OrientConnexSets(df, liste_arcs, target):
    """
    Oriente les arcs dans un graphe en fonction de la variable cible et de l'information mutuelle.

    Cette fonction identifie les composantes connexes du graphe, sélectionne une racine 
    pour chaque composante en fonction de l'information mutuelle avec la classe cible, 
    puis oriente les arcs en partant de cette racine en utilisant une recherche en profondeur (DFS).

    Paramètres
    ----------
    df : pandas.DataFrame
        Le DataFrame contenant les données.
    liste_arcs : list of tuple
        Une liste d'arcs non orientés, où chaque arc est représenté par un tuple (noeud1, noeud2, poids).
    target : str
        Le nom de la colonne représentant la variable cible.

    Retourne
    -------
    list of tuple
        Une liste d'arcs orientés, où chaque arc est représenté par un tuple (parent, enfant).
    """
    # Obtenir les composants connectés (ensembles)
    liste_ensembles = ConnexSets(liste_arcs)
    
    # Calculer l'information mutuelle entre chaque attribut et la classe
    mutual_info = {attr: MutualInformation(df, target, attr) for attr in df.columns if attr != target}
    
    # Initialiser la liste pour stocker les arcs orientés
    oriented_arcs = []
    
    # Itérer sur chaque ensemble et orienter les arcs
    for ensemble in liste_ensembles:
        # Sélectionner la racine en fonction de l'information mutuelle la plus élevée
        root = max(ensemble, key=lambda x: mutual_info[x])
        
        # Créer un graphe sous forme de liste d'adjacence (graphe non orienté)
        graph = {node: [] for node in ensemble}
        for arc in liste_arcs:
            node1, node2, _ = arc
            
            if node1 in ensemble and node2 in ensemble:
                graph[node1].append(node2)
                graph[node2].append(node1)
        
        # Effectuer une recherche en profondeur (DFS) pour orienter les arcs
        visited = set()
        
        def dfs(node, parent):
            # Visiter le nœud courant et orienter l'arc du parent vers le nœud
            if node in visited:
                return
            visited.add(node)
            
            if parent is not None:
                oriented_arcs.append((parent, node))  # Orienter l'arc du parent vers le nœud courant
            
            # Explorer tous les voisins du nœud courant
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, node)  # Visiter récursivement les voisins

        # Démarrer la recherche en profondeur depuis la racine
        dfs(root, None)
    
    return oriented_arcs

def P_cond(attr, value, parent, parent_value, df):
    """
    Calcule la probabilité conditionnelle P(attr=value | parent=parent_value).

    Paramètres
    ----------
    attr : str
        Le nom de la colonne représentant l'attribut enfant.
    value : Any
        La valeur de l'attribut enfant.
    parent : str
        Le nom de la colonne représentant l'attribut parent.
    parent_value : Any
        La valeur de l'attribut parent.
    df : pandas.DataFrame
        Le DataFrame contenant les données.

    Retourne
    -------
    float
        La probabilité conditionnelle. Retourne une valeur proche de zéro (1e-10)
        si le parent n'a aucune occurrence pour éviter une division par zéro.
    """
    subset = df[df[parent] == parent_value]
    count = subset[subset[attr] == value].shape[0]
    total = subset.shape[0]
    return count / total if total > 0 else 1e-10  # Avoid division by zero by using a small value




class MAPTANClassifier(APrioriClassifier):
    """
    Classifieur Tree-Augmented Naive Bayes (TAN) basé sur le maximum a posteriori (MAP).
    Cette classe utilise un modèle TAN où les attributs sont conditionnellement indépendants
    les uns des autres, sauf pour les relations représentées par un arbre.
    """
    
    def __init__(self, train_df):
        super().__init__(train_df)
        self.attributes = [col for col in train_df.columns if col != "target"]
        
        # Calculer les probabilités conditionnelles P(attr=a | target=t) pour chaque attribut
        self.p2d_l = {attr: P2D_l(train_df, attr) for attr in self.attributes}
        
        # Calculer les probabilités a priori de target
        self.prior = getPrior(train_df)["estimation"]
        
        # Calculer les probabilités marginales P(attr) pour chaque attribut
        self.p_attr = {attr: train_df[attr].value_counts(normalize=True).to_dict() for attr in self.attributes}
        
        # Initialize arcs and other TAN-specific structures
        self.cmis = np.array([[0 if x == y else ConditionalMutualInformation(self.train_df, x, y, "target") 
                               for x in self.train_df.keys() if x != "target"] for y in self.train_df.keys() if y != "target"])
        SimplifyConditionalMutualInformationMatrix(self.cmis)
        # self.liste_arcs = Kruskal(self.train_df, self.cmis)
        # pour tester avec le resultat trouver avec le prof
        self.liste_arcs = [('trestbps', 'chol', np.float64(0.6814942282235203)),
('age', 'trestbps', np.float64(0.641718295908513)),
('age', 'thalach', np.float64(0.6365766485465845)),
('chol', 'oldpeak', np.float64(0.5246930555244587)),
('oldpeak', 'slope', np.float64(0.25839871090530614)),
('chol', 'ca', np.float64(0.2528327956181666))]
        self.oriented_liste_arcs = OrientConnexSets(self.train_df, self.liste_arcs, 'target')
        self.arcs = ";".join([f"{'target'}->{col}" for col in self.train_df.columns if col != 'target'])
        self.arcs += ";" + ";".join([f"{u}->{v}" for u, v in self.oriented_liste_arcs])

    def estimProbas(self, attrs):
        """
        Estimate posterior probabilities P(target=0|attrs) and P(target=1|attrs)
        using TAN structure and MAP.
        """
        prob_0 = 1 - self.prior
        prob_1 = self.prior

        # Maintain a mapping of parent-child relationships
        parent_map = {child: parent for parent, child in self.oriented_liste_arcs}

        for attr in self.attributes:
            attr_value = attrs.get(attr, None)
            if attr_value is None:
                continue

            if attr not in parent_map:
                # Root attribute: P(attr | target)
                prob_0 *= self.p2d_l[attr][0].get(attr_value, 1e-10)
                prob_1 *= self.p2d_l[attr][1].get(attr_value, 1e-10)
            else:
                # Dependent attribute: P(child | parent, target)
                parent = parent_map[attr]
                parent_value = attrs.get(parent, None)
                if parent_value is not None:
                    prob_0 *= P_cond(attr, attr_value, parent, parent_value, self.train_df) * self.p2d_l[parent][0].get(parent_value, 1e-10)
                    prob_1 *= P_cond(attr, attr_value, parent, parent_value, self.train_df) * self.p2d_l[parent][1].get(parent_value, 1e-10)

        # Normalize probabilities
        total_prob = prob_0 + prob_1
        if total_prob == 0:
            return {0: 0.5, 1: 0.5}

        return {0: prob_0 / total_prob, 1: prob_1 / total_prob}

    def estimClass(self, attrs):
        """
        Estime la classe en utilisant les probabilités calculées par estimProbas.

        Args:
            attrs (dict): Un dictionnaire représentant un individu avec ses attributs.

        Returns:
            int: La classe estimée (0 ou 1).
        """
        probas = self.estimProbas(attrs)
        return 1 if probas[1] > probas[0] else 0


    def draw(self):
        """
        Visualiser la structure de l'arbre du modèle TAN en tant que graphe.
        """
        return drawGraph(self.arcs)

