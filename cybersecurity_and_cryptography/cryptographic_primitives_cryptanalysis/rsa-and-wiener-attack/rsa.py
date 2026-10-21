import random
import time

def euclide_etendu(a, b):
    u0, u1 = 1, 0
    v0, v1 = 0, 1
    while b != 0:
        q = a // b
        a, b = b, a % b
        u0, u1 = u1, u0 - q * u1
        v0, v1 = v1, v0 - q * v1
    return a, u0, v0

def rsa_chiffrement (x,N,e):
    return pow(x, e, N)

def rsa_dechiffrement (y,p,q,d):
    return pow(y, d, p * q)

# Retourne s tel que s % n1 == a1 et s % n2 == a2
def crt2 (a1,a2,n1,n2):
    g, u1, u2 = euclide_etendu(n1, n2)
    # on suppose qu'une solution existe
    n = (n1 * n2) // g
    s = (a1 * u2 * n2 + a2 * u1 * n1) // g
    return s % n, n

def rsa_dechiffrement_crt (y,p,q,up,uq,dp,dq,N):
    mp = pow(y % p, dp, p)
    mq = pow(y % q, dq, q)
    # recombinaison avec bezout (up*p + uq*q = 1)
    return (mp * uq * q + mq * up * p) % N

#### Wiener
def cfrac(a,b):
    L = []
    while b != 0:
        L.append(a // b)
        a, b = b, a % b
    return L

def reduite(L):
    # calcul des reduites par recurrence
    p0, p1 = 0, 1
    q0, q1 = 1, 0
    res = []
    for a in L:
        p0, p1 = p1, a * p1 + p0
        q0, q1 = q1, a * q1 + q0
        res.append((p1, q1))
    return res

def Wiener(m,c,N,e):
    L = cfrac(e, N)
    R = reduite(L)
    # on cherche d parmi les denominateurs des reduites
    for k, d in R:
        if d > 0 and pow(c, d, N) == m:
            return d
    return None


### Generation de premiers
def is_probable_prime(N, nbases=20):
    """
    True if N is a strong pseudoprime for nbases random bases b < N.
    Uses the Miller--Rabin primality test.
    """

    def miller(a, n):
        """
        Returns True if a proves that n is composite, False if n is probably prime in base n
        """

        def decompose(i, k=0):
            """
            decompose(n) returns (s,d) st. n = 2**s * d, d odd
            """
            if i % 2 == 0:
                return decompose(i // 2, k + 1)
            else:
                return (k, i)

        (s, d) = decompose(n - 1)
        x = pow(a, d, n)
        if (x == 1) or (x == n - 1):
            return False
        while s > 1:
            x = pow(x, 2, n)
            if x == n - 1:
                return False
            s -= 1
        return True

    if N == 2:
        return True
    for i in range(nbases):
        import random
        a = random.randint(2, N - 1)
        if miller(a, N):
            return False
    return True


def random_probable_prime(bits):
    """
    Returns a probable prime number with the given number of bits.
    Remarque : on est sur qu'un premier existe par le postulat de Bertrand
    """
    n = 1 << bits
    import random
    p = random.randint(n, 2 * n - 1)
    while (not (is_probable_prime(p))):
        p = random.randint(n, 2 * n - 1)
    return p


if __name__ == "__main__":
    # Ex 1 Q4 : comparaison des temps RSA vs RSA CRT
    print("Taille N | Temps RSA (s) | Temps CRT (s)")
    for bits in [256, 512, 1024, 2048, 4096]:
        p = random_probable_prime(bits // 2)
        q = random_probable_prime(bits // 2)
        N = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        while euclide_etendu(e, phi)[0] != 1:
            e = random.randint(3, phi - 1)

        _, d, _ = euclide_etendu(e, phi)
        d = d % phi
        dp = d % (p - 1)
        dq = d % (q - 1)
        _, up, uq = euclide_etendu(p, q)

        m = random.randint(2, N - 1)
        y = rsa_chiffrement(m, N, e)

        t0 = time.time()
        m1 = rsa_dechiffrement(y, p, q, d)
        t_rsa = time.time() - t0

        t0 = time.time()
        m2 = rsa_dechiffrement_crt(y, p, q, up, uq, dp, dq, N)
        t_crt = time.time() - t0

        assert m1 == m and m2 == m
        print(f"{bits:8d} | {t_rsa:13.6f} | {t_crt:13.6f}")

    # Ex 2 Q3 : test de Wiener en fonction de la taille de d
    print("\nTest Wiener (N = 1024 bits) :")
    p = random_probable_prime(512)
    q = random_probable_prime(512)
    N = p * q
    phi = (p - 1) * (q - 1)

    for bits_d in range(248, 260, 2):
        d = random_probable_prime(bits_d)
        while euclide_etendu(d, phi)[0] != 1:
            d = random_probable_prime(bits_d)

        _, e, _ = euclide_etendu(d, phi)
        e = e % phi

        m = random.randint(2, 10000)
        c = rsa_chiffrement(m, N, e)
        res = Wiener(m, c, N, e)
        print(f"d de {bits_d} bits : {'trouve' if res == d else 'echec'}")
