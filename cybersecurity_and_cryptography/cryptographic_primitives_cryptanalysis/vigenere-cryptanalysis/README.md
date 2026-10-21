# Lab 2: Vigenère Cipher Cryptanalysis

Implementation of the Vigenère cipher and three progressive statistical cryptanalysis techniques in Python (`cryptanalyse_vigenere.py`).

## Methodology

A Vigenère cipher with a key of length $k$ partitions the ciphertext into $k$ independent columns, each shifted by a Caesar cipher. Cryptanalysis proceeds in two phases: determining the key length $k$, then recovering the shift of each column.

1. **Method 1 — Index of Coincidence (IC) & Most Frequent Letter (`cryptanalyse_v1`)**
   * **Key length:** Tests candidate lengths $k \le 20$ by splitting the ciphertext into $k$ columns and computing their average Index of Coincidence ($IC = \frac{\sum n_i(n_i - 1)}{n(n - 1)}$). The first $k$ with an average $IC > 0.06$ (close to French text) is selected.
   * **Key recovery:** Treats each column independently and assumes its most frequent letter corresponds to `E`.

2. **Method 2 — Mutual Index of Coincidence (`cryptanalyse_v2`)**
   * **Key length:** Same IC threshold method ($IC > 0.06$).
   * **Key recovery:** Instead of relying on a single frequent letter per column (which fails on short columns), aligns columns $2 \dots k$ relative to the first column by finding the relative shift $d$ that maximizes the Mutual Index of Coincidence ($ICM = \frac{\sum n_{1,i} n_{2,i+d}}{n_1 n_2}$). Once aligned, the entire text is reduced to a single Caesar cipher.

3. **Method 3 — Pearson Linear Correlation (`cryptanalyse_v3`)**
   * **Joint key length & shift recovery:** For each candidate length $k \in [1, 20]$ and each column, computes the Pearson correlation coefficient between the unshifted column histogram and reference French letter frequencies (computed from Zola's *Germinal*). The key length and column shifts that maximize the average correlation across all columns are used to decrypt the text.
