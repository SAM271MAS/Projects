#!/usr/bin/env python3
"""
Automated cryptanalysis of monoalphabetic substitution ciphers
using hill-climbing and French tetragram log-likelihood scoring.
Usage: python3 crypt_auto_mono.py <ciphertext_file> [tetragram_csv]
"""

import csv
import math
import os
import random
import sys

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def get_data(f_name):
    """Load tetragram frequencies/counts from a semicolon-delimited CSV."""
    data_dict = {}
    with open(f_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) >= 2:
                data_dict[row[0]] = float(row[1])
    return data_dict


def calculate_e(text, frequencies):
    """Compute the log-likelihood score of a text based on its tetragrams."""
    e_value = 0.0
    for i in range(len(text) - 3):
        tetragram = text[i : i + 4]
        if tetragram in frequencies:
            e_value += math.log(frequencies[tetragram])
        else:
            e_value += math.log(0.001)
    return e_value


def random_swap(substitution, num_swaps=1):
    """Swap two randomly chosen characters in the substitution mapping."""
    letters = list(substitution.keys())
    for _ in range(num_swaps):
        a, b = random.sample(letters, 2)
        substitution[a], substitution[b] = substitution[b], substitution[a]
    return substitution


def apply_substitution(text, substitution):
    """Apply a character substitution dictionary to a string."""
    return "".join(substitution.get(char, char) for char in text)


def invert_substitution(substitution):
    """Return the inverse key string (encryption key from decryption mapping)."""
    inv = {v: k for k, v in substitution.items()}
    return "".join(inv[c] for c in ALPHABET)


def cryptanalyze(text, tetragram_frequencies, max_iterations=10000, patience=1000):
    """Hill-climbing search for the substitution that maximizes tetragram score."""
    best_substitution = {char: char for char in ALPHABET}
    best_e = calculate_e(
        apply_substitution(text, best_substitution), tetragram_frequencies
    )
    stagnant_iterations = 0
    iterations = 0

    while iterations < max_iterations and stagnant_iterations < patience:
        new_substitution = random_swap(best_substitution.copy(), num_swaps=1)
        new_text = apply_substitution(text, new_substitution)
        new_e = calculate_e(new_text, tetragram_frequencies)

        if new_e > best_e:
            best_substitution = new_substitution
            best_e = new_e
            stagnant_iterations = 0
        else:
            stagnant_iterations += 1

        iterations += 1

    return best_substitution, iterations


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 crypt_auto_mono.py <fichier_texte> <fichier_tetragrammes>")
        sys.exit(1)

    filename = sys.argv[1]
    tetra_file = sys.argv[2]

    try:
        with open(filename, "r", encoding="utf-8") as file:
            ciphertext = file.read().strip()
    except FileNotFoundError:
        print(f"Le fichier {filename} n'existe pas.")
        sys.exit(1)

    try:
        tetragram_frequencies = get_data(tetra_file)
    except FileNotFoundError:
        print(f"Le fichier {tetra_file} n'existe pas.")
        sys.exit(1)

    ciphertext_eval = calculate_e(ciphertext, tetragram_frequencies)
    best_substitution, total_iter = cryptanalyze(ciphertext, tetragram_frequencies)

    decryption_map = "".join(best_substitution[c] for c in ALPHABET)
    encryption_key = invert_substitution(best_substitution)
    plaintext = apply_substitution(ciphertext, best_substitution)
    plaintext_eval = calculate_e(plaintext, tetragram_frequencies)

    print("texte chiffré\n" + ciphertext)
    print("évaluation " + str(ciphertext_eval))
    print("\nAprès " + str(total_iter) + " itérations, texte déchiffré\n" + plaintext)
    print("substitution appliquée au texte fourni " + decryption_map)
    print("clef " + encryption_key)
    print("évaluation " + str(plaintext_eval))
