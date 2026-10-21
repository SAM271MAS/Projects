# Sorbonne Université 3I024 2024-2025
# TME 2 : Cryptanalyse du chiffre de Vigenere


import sys, getopt, string, math

# Alphabet français
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Fréquence moyenne des lettres en français
freq_FR = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# variables globales
ln_alphabet = len(alphabet)
ord_A = ord('A')


def frequence(filename: str) -> None:
    """
    Prendre le nom d'un fichier texte et modifier la variable globale freq_FR
    en calculant la fréquence d'apparition de chaque lettre de l'alphabet
    dans le contenu du fichier.

    Returns:
    None
    """

    occurrences = [0 for _ in range(ln_alphabet)]
    length = 0

    with open(filename, 'r') as file:
        content = file.read()

    for char in content:
        index = (ord(char) - ord_A)
        occurrences[index] += 1
        length += 1

    # Calcul des fréquences
    global freq_FR
    freq_FR = [occurrences[i] / len(content) for i in range(ln_alphabet)]


frequence("germinal_net.txt")


# Chiffrement César
def chiffre_cesar(txt: str, key: int) -> str:
    """
    Prendre un texte en clair et une clé, et retourner le texte chiffré en
    utilisant le chiffrement de César.

    Returns:
    str : le texte chiffré.
    """
    txt_chiffre = ""
    for char in txt:
        txt_chiffre += chr((ord(char) + key - ord_A) % ln_alphabet + ord_A)
    return txt_chiffre


# Déchiffrement César
def dechiffre_cesar(txt: str, key: int) -> str:
    """
    Prendre un texte chiffré et une clé, et retourner le texte déchiffré en
    utilisant le chiffrement de César.

    Returns:
    str : le texte déchiffré.
    """

    txt_dechiffre = ""
    for char in txt:
        txt_dechiffre += chr((ord(char) - key - ord_A) % ln_alphabet + ord_A)
    return txt_dechiffre


# Chiffrement Vigenere
def chiffre_vigenere(txt: str, key: int) -> str:
    """
    Prendre un texte en clair et une clé, et retourner le texte chiffré en
    utilisant le chiffrement de Vigenère.

    Returns:
    str : le texte chiffré.
    """
    taille_cle = len(key)
    txt_chiffre = ""
    for c in range(len(txt)):
        txt_chiffre += chr((ord(txt[c]) + key[c % taille_cle] - ord_A) % ln_alphabet + ord_A)

    return txt_chiffre


# Déchiffrement Vigenere
def dechiffre_vigenere(txt: str, key: int) -> str:
    """
    Prendre un texte chiffré et une clé, et retourner le texte déchiffré en
    utilisant le chiffrement de Vigenère.

    Returns:
    str : le texte déchiffré.
    """
    taille_cle = len(key)
    txt_dechiffre = ""
    for c in range(len(txt)):
        txt_dechiffre += chr((ord(txt[c]) - key[c % taille_cle] - ord_A) % ln_alphabet + ord_A)

    return txt_dechiffre


# Analyse de fréquences
def freq(txt: str) -> str:
    """
    Prendre un texte et retourner un histogramme représentant la fréquence
    d'apparition de chaque lettre dans ce texte

    Returns:
    list : une liste des entiers représentant la fréquence d'apparition de chaque lettre de l'alphabet.
    """
    hist = [0] * ln_alphabet
    for char in txt:
        hist[ord(char) - ord_A] += 1
    return hist


# Renvoie l'indice dans l'alphabet
# de la lettre la plus fréquente d'un texte
def lettre_freq_max(txt: str) -> int:
    """
    Prendre un texte et retourner l'indice de la lettre qui a la fréquence
    d'apparition la plus élevée.

    Returns:
    int : l'indice de la lettre avec la fréquence d'apparition la plus élevée.
    """
    temp_freq = freq(txt)
    return temp_freq.index(max(temp_freq))


# indice de coïncidence
def indice_coincidence(hist: list) -> float:
    """
    Prendre un histogramme des fréquences d'apparition des lettres et retourner l'indice de
    coïncidence.

    Returns:
    float : l'indice de coïncidence.
    """
    indice_coincid = 0.0
    n = 0
    for i in range(ln_alphabet):
        indice_coincid += (hist[i] * (hist[i] - 1))
        n += hist[i]

    return indice_coincid / (n * (n - 1))


# Recherche la longueur de la clé
def decouper_texte(text: str, longeur: int) -> list:
    """
    Prendre un texte et une longueur, et retourner une liste de chaînes de caractères
    chacune correspondant à une colonne de texte découpé selon la longueur spécifiée.
    Est utilisé dans d'autres fonctions pour rendre le code plus clair.

    Returns:
    list : une liste de chaînes de caractères représentant les colonnes découpées du texte.
    """

    colonnes = ['' for _ in range(longeur)]
    for i in range(len(text)):
        colonnes[i % longeur] += text[i]
    return colonnes


def longueur_clef(cipher: str) -> int:
    """
    Prendre un texte chiffré et déterminer la longueur probable de la clé
    de chiffrement en utilisant l'indice de coïncidence pour analyser
    les colonnes du texte.

    Returns:
    int : la longueur probable de la clé de chiffrement.
    """

    long_c_max = 20
    for i in range(1, long_c_max + 1):
        colonnes = decouper_texte(cipher, i)
        moy = sum([indice_coincidence(freq(col)) for col in colonnes]) / i
        if moy > 0.06:
            return i
    return 0


# Renvoie le tableau des décalages probables étant
# donné la longueur de la clé
# en utilisant la lettre la plus fréquente
# de chaque colonne
def clef_par_decalages(cipher: str, key_length: int) -> list:
    """
    Prendre un texte chiffré et une longueur de clé, et retourner une liste
    de décalages calculés en fonction des fréquences des lettres.

    Returns:
    list : une liste d'entiers représentant les décalages calculés.
    """
    decalages = [0] * key_length
    colonnes = decouper_texte(cipher, key_length)
    ord_e = ord('E') - ord_A
    for i, c in enumerate(colonnes):
        decalages[i] = (lettre_freq_max(c) - ord_e) % ln_alphabet

    return decalages


# Cryptanalyse V1 avec décalages par frequence max
def cryptanalyse_v1(cipher: str) -> str:
    """
    Prendre un texte chiffré et retourner le texte déchiffré en utilisant l'analyse des fréquences
    et les décalages calculés.

    Arguments:
    cipher (str) : le texte chiffré à analyser.

    Returns:
    str : le texte déchiffré.
    """
    ln_cle = longueur_clef(cipher)
    decalages = clef_par_decalages(cipher, ln_cle)

    return dechiffre_vigenere(cipher, decalages)


################################################################


### Les fonctions suivantes sont utiles uniquement
### pour la cryptanalyse V2.

# Indice de coincidence mutuelle avec décalage
def indice_coincidence_mutuelle(h1: list, h2: list, d: int) -> float:
    """
    Calculer l'indice de coïncidence mutuelle entre deux histogrammes de fréquences de lettres,
    en prenant en compte un décalage donné.

    Returns:
    float : l'indice de coïncidence mutuelle.
    """
    n_1 = 0
    n_2 = 0

    ind_coi_mut = 0.0

    for i in range(ln_alphabet):
        dec = (i + d) % ln_alphabet
        ind_coi_mut += (h1[i] * h2[dec])
        n_1 += h1[i]
        n_2 += h2[i]

    return ind_coi_mut / (n_1 * n_2)


# Renvoie le tableau des décalages probables étant
# donné la longueur de la clé
# en comparant l'indice de décalage mutuel par rapport
# à la première colonne
def tableau_decalages_ICM(cipher: str, key_length: int) -> list:
    """
    Renvoie le tableau des décalages probables étant donné la longueur de la clé, en comparant
    l'indice de coïncidence mutuelle par rapport à la première colonne.

    Returns:
    list : une liste d'entiers représentant les décalages probables.
    """
    decalages = [0] * key_length
    colonnes = decouper_texte(cipher, key_length)
    c1_freq = freq(colonnes[0])

    for i in range(1, key_length):
        # Calcul de l'indice de coïncidence mutuelle maximum et du meilleur décalage
        max_icm, best_d = max([(indice_coincidence_mutuelle(c1_freq, freq(colonnes[i]), d), d) for d in range(ln_alphabet)])
        decalages[i] = best_d

    return decalages


# Cryptanalyse V2 avec décalages par ICM
def cryptanalyse_v2(cipher):
    """
    Prendre un texte chiffré et retourner le texte déchiffré en utilisant une
    analyse des indice de coïncidence mutuelle.

    Returns:
    str : le texte déchiffré.
    """
    ln_cle = longueur_clef(cipher)
    decalages = tableau_decalages_ICM(cipher, ln_cle)
    aligned_txt = ""

    for i in range(len(cipher)):
        aligned_txt += dechiffre_cesar(cipher[i], decalages[i % ln_cle])

    ord_e = ord('E') - ord_A
    key = (lettre_freq_max(aligned_txt) - ord_e) % ln_alphabet

    return dechiffre_cesar(aligned_txt, key)


################################################################


### Les fonctions suivantes sont utiles uniquement
### pour la cryptanalyse V3.


# Prend deux listes de même taille et
# calcule la correlation lineaire de Pearson
def correlation(L1: list, L2: list) -> float:
    """
    Calculer la corrélation entre deux listes

    Returns:
    float : le coefficient de corrélation entre les deux listes.
    """
    n = len(L1)
    mean_L1 = 0
    mean_L2 = 0

    for i in range(n):
        mean_L1 += L1[i]
        mean_L2 += L2[i]

    mean_L1 /= n
    mean_L2 /= n
    s1 = 0
    s2 = 0
    s3 = 0

    for i in range(n):
        s1 += (L1[i] - mean_L1) * (L2[i] - mean_L2)
        s2 += ((L1[i] - mean_L1)**2)
        s3 += ((L2[i] - mean_L2)**2)

    return round(s1 / (math.sqrt(s2) * math.sqrt(s3)), 10)


# Renvoie la meilleur clé possible par correlation
# étant donné une longueur de clé fixée
def clef_correlations(cipher: str, key_length: int) -> tuple:
    """
    Calculer les clés de chiffrement en trouvant la meilleure corrélation entre la fréquence des lettres françaises
    et les lettres décalées du texte chiffré, en utilisant la longueur de la clé.

    Returns:
    tuple : un tuple contenant le score de corrélation moyen et la clé de chiffrement.
    """

    key = [0] * key_length
    score = 0.0

    colonnes = decouper_texte(cipher, key_length)

    for i in range(key_length):
        max_corr = 0
        best_d = 0

        for j in range(ln_alphabet):
            temp_corr = correlation(freq_FR, freq(dechiffre_cesar(colonnes[i], j)))
            if temp_corr > max_corr:
                max_corr = temp_corr
                best_d = j
        key[i] = best_d
        score += max_corr

    score /= key_length
    return (score, key)


# Cryptanalyse V3 avec correlations
def cryptanalyse_v3(cipher: str) -> str:
    """
    Analyser un texte chiffré et déterminer la clé de chiffrement en trouvant la meilleure corrélation
    entre les fréquences des lettres françaises et les colonnes du texte chiffré.
    Utiliser cette clé pour déchiffrer le texte.

    Returns:
    str : le texte déchiffré.
    """
    cle_taille_max = 20
    max_corr = 0
    key = []
    for tc in range(1, cle_taille_max + 1):
        tmp_corr, tmp_key = clef_correlations(cipher, tc)
        if tmp_corr > max_corr:
            max_corr = tmp_corr
            key = tmp_key

    return dechiffre_vigenere(cipher, key)


# Lit un fichier et renvoie la chaine de caracteres
def read(fichier):
    f=open(fichier,"r")
    txt=(f.readlines())[0].rstrip('\n')
    f.close()
    return txt

# Execute la fonction cryptanalyse_vN où N est la version
def cryptanalyse(fichier, version):
    cipher = read(fichier)
    if version == 1:
        return cryptanalyse_v1(cipher)
    elif version == 2:
        return cryptanalyse_v2(cipher)
    elif version == 3:
        return cryptanalyse_v3(cipher)

def usage():
    print ("Usage: python3 cryptanalyse_vigenere.py -v <1,2,3> -f <FichierACryptanalyser>", file=sys.stderr)
    sys.exit(1)

def main(argv):
    size = -1
    version = 0
    fichier = ''
    try:
        opts, args = getopt.getopt(argv,"hv:f:")
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-v"):
            version = int(arg)
        elif opt in ("-f"):
            fichier = arg
    if fichier=='':
        usage()
    if not(version==1 or version==2 or version==3):
        usage()

    print("Cryptanalyse version "+str(version)+" du fichier "+fichier+" :")
    print(cryptanalyse(fichier, version))
    
if __name__ == "__main__":
   main(sys.argv[1:])
