#!/usr/bin/env python3
"""
Compute and display the relative frequency of each uppercase ASCII letter (A-Z).
Usage: python3 frequence.py [fichier_texte]
"""

import sys

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def compute_frequencies(content):
    occurrences = {}
    length = 0
    for char in content:
        if char in ALPHABET:
            occurrences[char] = occurrences.get(char, 0) + 1
            length += 1

    if length == 0:
        return {c: 0.0 for c in ALPHABET}

    return {c: occurrences.get(c, 0) / length for c in ALPHABET}


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        try:
            with open(filename, "r", encoding="utf-8") as file:
                text = file.read()
        except FileNotFoundError:
            print(f"Le fichier {filename} n'existe pas.", file=sys.stderr)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    freqs = compute_frequencies(text)
    for c in ALPHABET:
        print(c, freqs[c])
