from math import sqrt
from random import choice, randint
import matplotlib.pyplot as plt


def exp(a, N, p):
    """Renvoie a**N % p par exponentiation rapide."""
    def binaire(N):
        L = []
        while N > 0:
            L.append(N % 2)
            N = N // 2
        L.reverse()
        return L

    res = 1
    for Ni in binaire(N):
        res = (res * res) % p
        if Ni == 1:
            res = (res * a) % p
    return res


def factor(n):
    """Renvoie la liste des couples (p, a_p) de la décomposition en facteurs premiers de n."""
    def factor_gen(n):
        j = 2
        while n > 1:
            for i in range(j, int(sqrt(n)) + 1):
                if n % i == 0:
                    n //= i
                    j = i
                    yield i
                    break
            else:
                if n > 1:
                    yield n
                    break

    factors_with_multiplicity = list(factor_gen(n))
    factors_set = sorted(set(factors_with_multiplicity))
    return [(p, factors_with_multiplicity.count(p)) for p in factors_set]


def inv_mod(x, p):
    """Renvoie l'inverse de x modulo p (par le petit théorème de Fermat)."""
    return exp(x, p - 2, p)


def racine_carree(a, p):
    """Renvoie une racine carrée de a mod p si p = 3 mod 4."""
    assert p % 4 == 3, "erreur: p != 3 mod 4"
    return exp(a, (p + 1) // 4, p)


def est_elliptique(E):
    """
    Renvoie True si la courbe E = (p, a, b) d'équation y^2 = x^3 + ax + b sur F_p
    est non-singulière (discriminant non nul mod p).
    """
    p, a, b = E
    return (4 * (a**3) + 27 * (b**2)) % p != 0


def point_sur_courbe(P, E):
    """Renvoie True si le point P appartient à la courbe E et False sinon."""
    if P == ():
        return True
    p, a, b = E
    x, y = P
    return (y**2) % p == (x**3 + a * x + b) % p


def symbole_legendre(a, p):
    """Renvoie le symbole de Legendre de a mod p (a^(p-1)/2 mod p)."""
    return exp(a, (p - 1) // 2, p)


def cardinal(E):
    """Renvoie le cardinal du groupe de points de la courbe E."""
    p, a, b = E
    card = 1
    for x in range(p):
        z = (x**3 + a * x + b) % p
        sym = symbole_legendre(z, p)
        if sym in [0, 1]:
            card += 1 + sym
    return card


def liste_points(E):
    """Renvoie la liste des points de la courbe elliptique E (pour p = 3 mod 4)."""
    p, a, b = E
    assert p % 4 == 3, "erreur: p n'est pas congru à 3 mod 4."

    liste_pt = [()]
    for x in range(p):
        z = (x**3 + a * x + b) % p
        sy_leg = symbole_legendre(z, p)
        if sy_leg == 1:
            y = racine_carree(z, p)
            liste_pt.append((x, y))
            liste_pt.append((x, (-y) % p))
        elif sy_leg == 0:
            liste_pt.append((x, 0))

    return liste_pt


def cardinaux_courbes(p):
    """
    Renvoie un dictionnaire D où D[c] contient le nombre de courbes elliptiques
    définies sur F_p ayant pour cardinal c (illustrant la borne de Hasse).
    """
    bound = int(2 * sqrt(p))
    D = {c: 0 for c in range(p + 1 - bound, p + 1 + bound + 1)}
    for a in range(p):
        for b in range(p):
            E = (p, a, b)
            if est_elliptique(E):
                c = cardinal(E)
                D[c] = D.get(c, 0) + 1
    return D


def dessine_graphe(p):
    """Dessine l'histogramme des cardinaux des courbes elliptiques définies sur F_p."""
    bound = int(2 * sqrt(p))
    C = [c for c in range(p + 1 - bound, p + 1 + bound + 1)]
    D = cardinaux_courbes(p)

    plt.bar(C, [D[c] for c in C], color="b")
    plt.show()


def moins(P, p):
    """Retourne l'opposé du point P mod p."""
    if P == ():
        return ()
    x, y = P
    return (x % p, (-y) % p)


def est_egal(P1, P2, p):
    """Teste l'égalité de deux points mod p."""
    if P1 == () and P2 == ():
        return True
    if P1 == () or P2 == ():
        return False
    x1, y1 = P1
    x2, y2 = P2
    return x1 % p == x2 % p and y1 % p == y2 % p


def est_zero(P):
    """Teste si un point est égal au point à l'infini."""
    return P == ()


def addition(P1, P2, E):
    """Renvoie P1 + P2 sur la courbe E."""
    if est_zero(P1):
        return P2
    if est_zero(P2):
        return P1

    p, a, _ = E
    if est_egal(P1, moins(P2, p), p):
        return ()

    x1, y1 = P1
    x2, y2 = P2

    if est_egal(P1, P2, p):
        inv = inv_mod(2 * y1, p)
        lam = (3 * (x1**2) + a) * inv % p
    else:
        inv = inv_mod(x2 - x1, p)
        lam = (y2 - y1) * inv % p

    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def multiplication_scalaire(k, P, E):
    """Renvoie la multiplication scalaire [k]P sur la courbe E (double-and-add)."""
    p, _, _ = E
    if k < 0:
        return moins(multiplication_scalaire(-k, P, E), p)

    res = ()
    Q = P
    while k:
        if k & 1:
            res = addition(res, Q, E)
        Q = addition(Q, Q, E)
        k //= 2
    return res


def ordre(N, factors_N, P, E):
    """
    Renvoie l'ordre du point P sur la courbe E mod p, étant donnés le cardinal N
    de la courbe et la factorisation de N en facteurs premiers.
    """
    if est_zero(P):
        return 1
    p_mod = E[0]
    d = N
    for q, a_q in factors_N:
        for _ in range(a_q):
            if est_egal(multiplication_scalaire(d // q, P, E), (), p_mod):
                d //= q
            else:
                break
    return d


def point_aleatoire_naif(E):
    """Tire aléatoirement des couples (x, y) dans F_p^2 jusqu'à tomber sur la courbe E (complexité O(p))."""
    p, _, _ = E
    while True:
        P = (randint(0, p - 1), randint(0, p - 1))
        if point_sur_courbe(P, E):
            return P


def point_aleatoire(E):
    """
    Tire aléatoirement x dans F_p et calcule sa racine carrée y lorsque x^3 + ax + b
    est un résidu quadratique (complexité O(log p) pour p = 3 mod 4).
    """
    p, a, b = E
    while True:
        x = randint(0, p - 1)
        z = (x**3 + a * x + b) % p
        leg = symbole_legendre(z, p)
        if leg == 1:
            y = racine_carree(z, p)
            return (x, choice([y, (-y) % p]))
        elif leg == 0:
            return (x, 0)


def point_ordre(E, N, factors_N, n):
    """Renvoie un point aléatoire d'ordre n (où n divise N) sur la courbe E."""
    while True:
        P = point_aleatoire(E)
        Q = multiplication_scalaire(N // n, P, E)
        if not est_zero(Q) and ordre(N, factors_N, Q, E) == n:
            return Q


def keygen_DH(P, E, n):
    """Génère une paire de clés (secrète, publique) pour l'échange Diffie-Hellman sur E."""
    sec = randint(1, n - 1)
    pub = multiplication_scalaire(sec, P, E)
    return (sec, pub)


def echange_DH(sec_A, pub_B, E):
    """Calcule le secret partagé [sec_A]pub_B lors d'un échange Diffie-Hellman."""
    return multiplication_scalaire(sec_A, pub_B, E)


if __name__ == "__main__":
    p = 248301763022729027652019747568375012323
    N = 248301763022729027652019747568375012324
    factors_N = [(2, 2), (62075440755682256913004936892093753081, 1)]
    E = (p, 1, 0)

    # Sous-groupe d'ordre premier maximal q = N // 4
    q = factors_N[1][0]
    P = point_ordre(E, N, factors_N, q)
    print("Point générateur d'ordre premier q pour ECDH :", P)
