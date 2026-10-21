#!/usr/bin/python3

import sys

# Usage: python3 subst_mono.py clef c/d phrase
# Returns the result without additional text


def generate_substitution_key(key):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    substitution_key = {}
    for i in range(len(alphabet)):
        substitution_key[alphabet[i]] = key[i]
    return substitution_key


def chiffrer_texte(texte, key):
    substitution_key = generate_substitution_key(key)
    texte_chiffre = ""
    for char in texte:
        if char in substitution_key:
            texte_chiffre += substitution_key[char]
        else:
            texte_chiffre += char
    return texte_chiffre


def dechiffrer_texte(texte, key):
    substitution_key = generate_substitution_key(key)
    reverse_key = {v: k for k, v in substitution_key.items()}
    texte_dechiffre = ""
    for char in texte:
        if char in reverse_key:
            texte_dechiffre += reverse_key[char]
        else:
            texte_dechiffre += char
    return texte_dechiffre


if len(sys.argv) < 4:
    print("Usage: python3 subst_mono.py cle c/d texte")
    sys.exit(1)

cle = sys.argv[1]
mode = sys.argv[2]
phrase = sys.argv[3]

if mode == 'c':
    print(chiffrer_texte(phrase, cle))
else:
    print(dechiffrer_texte(phrase, cle))
