Implementation of the RSA cryptosystem, Chinese Remainder Theorem (CRT) decryption acceleration, and Wiener's continued-fraction cryptanalysis in Python (`rsa.py`).

## Methodology

1. **Standard RSA vs. RSA-CRT (`rsa_chiffrement`, `rsa_dechiffrement`, `crt2`, `rsa_dechiffrement_crt`)**
   * **Standard RSA:** Encrypts via $c \equiv m^e \pmod N$ and decrypts via $m \equiv c^d \pmod N$ where $N = pq$ and $ed \equiv 1 \pmod{\phi(N)}$.
   * **CRT Decryption:** Instead of computing a full modular exponentiation modulo $N$, computes two half-sized exponentiations modulo $p$ and $q$ using reduced exponents $d_p = d \bmod (p-1)$ and $d_q = d \bmod (q-1)$:
     
     $m_p = (c \bmod p)^{d_p} \bmod p, \quad m_q = (c \bmod q)^{d_q} \bmod q$
     
     Recombines $(m_p, m_q)$ modulo $N$ using Bézout coefficients $u_p p + u_q q = 1$, achieving roughly a $3\times$ to $4\times$ speedup on large moduli (256 to 4096 bits).

2. **Wiener's Low Private Exponent Attack (`cfrac`, `reduite`, `Wiener`)**
   * When the private exponent $d$ is too small ( $d < \frac{1}{3}N^{1/4}$ ), the relation $ed - k\phi(N) = 1$ yields $\left\vert{}\frac{e}{N} - \frac{k}{d}\right\vert{} < \frac{1}{2d^2}$.
   * By Legendre's theorem, $\frac{k}{d}$ appears among the convergents (*réduites*) of the continued fraction expansion of $\frac{e}{N}$.
   * `cfrac` and `reduite` compute the continued fraction coefficients and convergents $(k_i, d_i)$ of $\frac{e}{N}$, and `Wiener` recovers the secret key $d$ in polynomial time by testing $c^{d_i} \equiv m \pmod N$.
