# Lab 1: Monoalphabetic Ciphers

Implementations of classical monoalphabetic encryption schemes and statistical cryptanalysis in Python ( works on uppercase ASCII texts `A-Z`).

## Scripts & Usage

* **`frequence.py`** — Computes the frequency of each letter (`A-Z`) in a text file.
```bash
  python3 frequence.py <text_file>

```

* **`cesar.py`** — Encrypts (`c`) or decrypts (`d`) a string using the Caesar cipher with a single key letter (`A-Z`).
```bash
python3 cesar.py D c BONJOUR
python3 cesar.py D d ERQMRXU

```

* **`subst_mono.py`** — Encrypts (`c`) or decrypts (`d`) a string using a 26-letter substitution alphabet.
```bash
python3 subst_mono.py QWERTYUIOPASDFGHJKLZXCVBNM c BONJOUR
python3 subst_mono.py QWERTYUIOPASDFGHJKLZXCVBNM d WGFPGXK

```

* **`crypt_auto_mono.py`** — Automated hill-climbing cryptanalysis of a monoalphabetic substitution cipher using 4-gram (tetragram) log-likelihood scoring from a reference frequency CSV (`TETRAGRAM;COUNT`).
```bash
  python3 crypt_auto_mono.py <ciphertext_file> <tetragram_csv>
```
