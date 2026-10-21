from math import ceil, sqrt
import random
from prime import is_probable_prime, random_probable_prime


# Exercice 1
# Q1: Extended Euclidean Algorithm (a*u + b*v = gcd(a, b))
def bezout(a, b):
    prev_r, r = a, b
    prev_u, u = 1, 0
    prev_v, v = 0, 1

    while r != 0:
        q = prev_r // r
        prev_r, r = r, prev_r - q * r
        prev_u, u = u, prev_u - q * u
        prev_v, v = v, prev_v - q * v

    return prev_r, prev_u, prev_v


# Q2: Modular Inverse & Invertible Elements of Z/NZ
def inv_mod(a, n):
    r, u, _ = bezout(a, n)
    if r == 1:
        return u % n
    return None


def invertibles(N):
    invertible_elements = []
    for i in range(1, N):
        if inv_mod(i, N) is not None:
            invertible_elements.append(i)
    return invertible_elements


# Q3: Euler's Totient Function phi(N)
def phi(N):
    return len(invertibles(N))


# Exercice 2
# Q1: Iterative Modular Exponentiation (a^n mod p)
def exp(a, n, p):
    res = 1
    base = a % p
    while n > 0:
        if n % 2 == 1:
            res = (res * base) % p
        base = (base * base) % p
        n //= 2
    return res


# Q2: Prime Factorization -> returns list of (prime, exponent) pairs
def factor(n):
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            count = 0
            while n % d == 0:
                n //= d
                count += 1
            factors.append((d, count))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors


# Q3: Multiplicative Order of a in (Z/pZ)* given the factorization of p - 1
def order(a, p, factors_p_minus1):
    t = p - 1
    for q, v_q in factors_p_minus1:
        for _ in range(v_q):
            if exp(a, t // q, p) == 1:
                t //= q
            else:
                break
    return t


# Q4: Find a Generator of the Cyclic Group (Z/pZ)*
def find_generator(p, factors_p_minus1):
    while True:
        g = random.randint(2, p - 1)
        if order(g, p, factors_p_minus1) == p - 1:
            return g


# Exercice 3: Generate a k-bit Safe Prime p = 2q + 1
def generate_safe_prime(k):
    while True:
        q = random_probable_prime(k - 1)
        p = 2 * q + 1
        if is_probable_prime(p):
            return p


# Exercice 4: Shanks' Baby-Step Giant-Step (solves g^x = n mod p)
def bsgs(n, g, p):
    s = ceil(sqrt(p - 1))

    # Baby steps
    baby_steps = {}
    current = 1
    for j in range(s):
        baby_steps[current] = j
        current = (current * g) % p

    # Giant steps
    g_inv = inv_mod(g, p)
    g_minus_s = exp(g_inv, s, p)
    giant_step = n % p

    for i in range(s + 1):
        if giant_step in baby_steps:
            return i * s + baby_steps[giant_step]
        giant_step = (giant_step * g_minus_s) % p

    return None
