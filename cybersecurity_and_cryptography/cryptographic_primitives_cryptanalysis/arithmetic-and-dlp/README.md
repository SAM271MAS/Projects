# Lab 3: Modular Arithmetic & Discrete Logarithm Problem (DLP)

Implementation of core modular arithmetic primitives, cyclic group operations in $(\mathbb{Z}/p\mathbb{Z})^\times$, and Shanks' Baby-Step Giant-Step algorithm in Python (`dlp.py`, using Miller-Rabin primality testing in `prime.py`).

## Methodology & Implemented Functions

1. **Modular Arithmetic (`bezout`, `inv_mod`, `invertibles`, `phi`)**
   * Uses the **Extended Euclidean Algorithm** to compute $\gcd(a, b)$ and Bézout coefficients $(u, v)$ such that $au + bv = \gcd(a, b)$.
   * Deduces modular inverses $a^{-1} \pmod n$ when $\gcd(a, n) = 1$, enumerates the multiplicative group $(\mathbb{Z}/N\mathbb{Z})^\times$, and computes Euler's totient function $\phi(N)$.

2. **Cyclic Group Instantiation (`exp`, `factor`, `order`, `find_generator`, `generate_safe_prime`)**
   * **Fast Exponentiation (`exp`):** Iterative square-and-multiply algorithm computing $a^n \bmod p$ in $\mathcal{O}(\log n)$ multiplications.
   * **Element Order & Generators (`order`, `find_generator`):** Given the prime factorization of $p - 1 = \prod q_i^{v_i}$, determines the exact multiplicative order of $a \in (\mathbb{Z}/p\mathbb{Z})^\times$ by testing divisors of $p - 1$, and finds primitive roots (generators of order $p - 1$).
   * **Safe Primes (`generate_safe_prime`):** Generates primes of the form $p = 2q + 1$ (where $q$ is a Germain prime) using the Miller-Rabin probabilistic test (`prime.py`) so $(\mathbb{Z}/p\mathbb{Z})^\times$ resists Pohlig-Hellman subgroup attacks.

3. **Shanks' Baby-Step Giant-Step (`bsgs`)**
   * Solves the Discrete Logarithm Problem $g^x \equiv n \pmod p$ in $\mathcal{O}(\sqrt{p})$ time and space by writing $x = i \cdot s + j$ with $s = \lceil \sqrt{p - 1} \rceil$.
   * **Baby steps:** Precomputes a hash table of $g^j \bmod p$ for $0 \le j < s$.
   * **Giant steps:** Iteratively computes $n \cdot (g^{-s})^i \bmod p$ for $0 \le i \le s$ until a collision with the baby-step table is found.
