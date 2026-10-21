#!/usr/bin/env python3
"""
Caesar cipher encryption and decryption.
Usage: python3 cesar.py <key_letter> <c|d> <phrase>
"""

import sys


def chiffrer_cesar(texte, cle):
    decalage = ord(cle.upper()) - ord("A")
    texte_chiffre = ""
    for char in texte:
        if "A" <= char <= "Z":
            texte_chiffre += chr(ord("A") + (ord(char) - ord("A") + decalage) % 26)
        else:
            texte_chiffre += char
    return texte_chiffre


def dechiffrer_cesar(texte, cle):
    decalage = ord(cle.upper()) - ord("A")
    texte_dechiffre = ""
    for char in texte:
        if "A" <= char <= "Z":
            texte_dechiffre += chr(ord("A") + (ord(char) - ord("A") - decalage) % 26)
        else:
            texte_dechiffre += char
    return texte_dechiffre


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 cesar.py clef c/d phrase")
        sys.exit(1)

    cle = sys.argv[1]
    mode = sys.argv[2]
    phrase = sys.argv[3]

    if mode == "c":
        print(chiffrer_cesar(phrase, cle))
    else:
        print(dechiffrer_cesar(phrase, cle))
