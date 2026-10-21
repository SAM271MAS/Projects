Implementation of elliptic curve arithmetic over finite fields $\mathbb{F}_p$ and the Elliptic Curve Diffie-Hellman (ECDH) key exchange protocol in Python (`ecc.py`).

## Methodology

Curves are represented in short Weierstrass form $\mathcal{E}: y^2 \equiv x^3 + ax + b \pmod p$ over $\mathbb{F}_p$ ( $p > 3$ ) with discriminant $\Delta = -16(4a^3 + 27b^2) \not\equiv 0 \pmod p$, and the point at infinity $\mathcal{O}$ is denoted by `()`.

1. **Curve Cardinality & Point Enumeration (`est_elliptique`, `symbole_legendre`, `cardinal`, `liste_points`, `cardinaux_courbes`)**
   * Uses **Euler's criterion** ( $\left(\frac{z}{p}\right) \equiv z^{(p-1)/2} \pmod p$ ) to test whether $z = x^3 + ax + b$ is a quadratic residue in $\mathbb{F}_p$, counting curve points via $\vert{}E(\mathbb{F}_p)\vert{} = 1 + \sum_{x \in \mathbb{F}_p} \left(1 + \left(\frac{x^3+ax+b}{p}\right)\right)$.
   * When $p \equiv 3 \pmod 4$, computes square roots directly via $y \equiv z^{(p+1)/4} \pmod p$.
   * Verifies **Hasse's Theorem** ( $\vert{}\#E(\mathbb{F}_p) - (p + 1)\vert{} \le 2\sqrt{p}$ ) across all elliptic curves over $\mathbb{F}_p$.

2. **Group Law & Scalar Multiplication (`addition`, `multiplication_scalaire`, `ordre`)**
   * Implements chord-and-tangent point addition and point doubling over $\mathbb{F}_p$ using modular inversion via Fermat's Little Theorem ( $x^{-1} \equiv x^{p-2} \pmod p$ ).
   * Computes scalar multiplication $[k]P$ in $\mathcal{O}(\log k)$ group operations using the **double-and-add** algorithm.
   * Determines the exact order of a point $P$ given the prime factorization of $N = \#E(\mathbb{F}_p)$.

3. **Random Point Sampling & ECDH Key Exchange (`point_aleatoire`, `point_ordre`, `keygen_DH`, `echange_DH`)**
   * Replaces naive $\mathcal{O}(p)$ rejection sampling on $(x, y) \in \mathbb{F}_p^2$ with $\mathcal{O}(\log p)$ sampling by picking $x \in \mathbb{F}_p$ until $x^3 + ax + b$ is a quadratic residue and extracting its modular square root.
   * Generates points of large prime order $q \mid \#E(\mathbb{F}_p)$ via cofactor clearing ( $Q = [N/q]P$ ) to instantiate a secure **Elliptic Curve Diffie-Hellman (ECDH)** key exchange resistant to Pohlig-Hellman attacks.
