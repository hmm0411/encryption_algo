import string
from collections import Counter
import math

alphabet = "abcdefghijklmnopqrstuvwxyz"

# English unigram frequencies
english_freq = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702,
    'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153,
    'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507,
    'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974,
    'z': 0.00074
}

# 1. Index of Coincidence
def IC(text):
    text = [c for c in text if c in alphabet]
    N = len(text)
    if N < 2:
        return 0
    cnt = Counter(text)
    return sum(v * (v - 1) for v in cnt.values()) / (N * (N - 1))


# 2. Kasiski Examination
def kasiski(cipher):
    cipher = cipher.lower()
    sequences = {}
    seq_len = 3  # trigram

    for i in range(len(cipher) - seq_len):
        seq = cipher[i:i+seq_len]
        if all(c in alphabet for c in seq):
            sequences.setdefault(seq, []).append(i)

    spacings = []
    for seq, pos in sequences.items():
        if len(pos) >= 2:
            for i in range(len(pos)-1):
                spacings.append(pos[i+1] - pos[i])

    if not spacings:
        return []

    from math import gcd
    gcds = []
    for a in spacings:
        for b in spacings:
            if a != b:
                g = gcd(a, b)
                if 2 <= g <= 20:
                    gcds.append(g)

    return gcds


# 3. Estimate key length using Kasiski + IC
def guess_key_len(cipher, max_len=20):
    cipher = cipher.lower()

    kasiski_guess = kasiski(cipher)

    best_len = 1
    best_score = 0

    for m in range(1, max_len+1):
        subsets = [cipher[i::m] for i in range(m)]
        avg_ic = sum(IC(s) for s in subsets) / m

        # Prioritize Kasiski candidates
        if kasiski_guess and any(abs(m - g) <= 1 for g in kasiski_guess):
            avg_ic *= 1.1

        if avg_ic > best_score:
            best_score = avg_ic
            best_len = m

    return best_len


# 4. Chi-square scoring for Caesar shift
def chi_square(subset, shift):
    subset = [c for c in subset if c in alphabet]
    shifted = [(ord(c) - 97 - shift) % 26 for c in subset]
    letters = ''.join(chr(v + 97) for v in shifted)

    N = len(letters)
    if N == 0:
        return 1e9

    cnt = Counter(letters)
    chi = 0
    for c in alphabet:
        observed = cnt[c]
        expected = english_freq[c] * N
        chi += (observed - expected) ** 2 / expected

    return chi


def best_shift(subset):
    best_s = 0
    best_val = 1e9
    for s in range(26):
        v = chi_square(subset, s)
        if v < best_val:
            best_val = v
            best_s = s
    return best_s


# 5. Decrypt with a given key
def decrypt(cipher, key):
    out = []
    m = len(key)
    idx = 0

    for c in cipher:
        if c.lower() in alphabet:
            shift = ord(key[idx % m]) - 97
            if c.isupper():
                base = 65
            else:
                base = 97
            out.append(chr((ord(c) - base - shift) % 26 + base))
            idx += 1
        else:
            out.append(c)

    return ''.join(out)


# 6. Refine key using hill-climbing
def refine_key(cipher, key):

    def english_score(text):
        return sum(english_freq.get(c, 0) for c in text.lower())

    key = list(key)
    best_plain = decrypt(cipher, ''.join(key))
    best_score = english_score(best_plain)

    improved = True
    while improved:
        improved = False

        for i in range(len(key)):
            old = key[i]
            for s in range(26):
                key[i] = chr(97 + s)
                new_plain = decrypt(cipher, ''.join(key))
                new_score = english_score(new_plain)

                if new_score > best_score:
                    best_score = new_score
                    improved = True
                    break

                key[i] = old

    return ''.join(key)


# 7. MAIN SOLVER (for Dashboard)
def vigenere_auto_decrypt(ciphertext):
    key_len = guess_key_len(ciphertext)

    # initial key guess
    key = ""
    for i in range(key_len):
        subset = ''.join(ciphertext[j] for j in range(i, len(ciphertext), key_len))
        shift = best_shift(subset)
        key += chr((26 - shift) % 26 + 97)

    # refine key
    key = refine_key(ciphertext, key)

    plaintext = decrypt(ciphertext, key)
    return key, plaintext
