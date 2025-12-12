# ==========================================================
#   LAB06 - TASK 2 - MONOALPHABETIC SUBSTITUTION CIPHER
#   Full version for Streamlit Dashboard
# ==========================================================

import math
import random
from collections import Counter

# ----------------------------
# English n-gram frequencies
# ----------------------------

UNIGRAM = {
    'e': 0.127, 't': 0.091, 'a': 0.082, 'o': 0.075, 'i': 0.070,
    'n': 0.067, 's': 0.063, 'h': 0.061, 'r': 0.060, 'd': 0.043,
    'l': 0.040, 'c': 0.028, 'u': 0.028, 'm': 0.024, 'w': 0.023,
    'f': 0.022, 'g': 0.020, 'y': 0.020, 'p': 0.019, 'b': 0.015,
    'v': 0.009, 'k': 0.008, 'x': 0.0015, 'j': 0.0015,
    'q': 0.001, 'z': 0.0007
}

BIGRAM = {
    "th": 0.0356, "he": 0.0307, "in": 0.0243, "er": 0.0205,
    "an": 0.0199, "re": 0.0185, "on": 0.0176, "at": 0.0149,
    "en": 0.0145, "nd": 0.0135, "ti": 0.0134, "es": 0.0134,
    "or": 0.0128, "te": 0.0120, "of": 0.0117
}

DEFAULT_UNI = 1e-6
DEFAULT_BI = 1e-7


# ==========================================================
# SCORING FUNCTION
# ==========================================================
def score_text(text):
    text = text.lower()
    score = 0.0

    # unigram
    for c in text:
        if 'a' <= c <= 'z':
            score += UNIGRAM.get(c, DEFAULT_UNI)

    # bigram
    for i in range(len(text) - 1):
        bg = text[i:i+2]
        score += BIGRAM.get(bg, DEFAULT_BI)

    return score


# ==========================================================
# TRANSLATION FUNCTIONS
# ==========================================================
def build_translate_table(mapping):
    table = {i: i for i in range(256)}

    for k, v in mapping.items():
        table[ord(k)] = ord(v)
        table[ord(k.upper())] = ord(v.upper())

    return table


def apply_mapping(ciphertext, table):
    return ciphertext.translate(table)


# ==========================================================
# INITIAL MAPPING (FREQUENCY ANALYSIS)
# ==========================================================
def seed_mapping(cipher):
    freq = Counter([c for c in cipher if 'a' <= c <= 'z'])
    ordered = [c for c, _ in freq.most_common()]

    english_order = "etaoinshrdlucmfwypvbgkjqxz"

    mapping = {}

    for i, c in enumerate(ordered):
        mapping[c] = english_order[i]

    # fill unused letters
    used = set(mapping.values())
    remaining = [c for c in english_order if c not in used]

    for c in "abcdefghijklmnopqrstuvwxyz":
        if c not in mapping:
            mapping[c] = random.choice(remaining)

    return mapping


# ==========================================================
# RANDOM SWAP
# ==========================================================
def random_swap(mapping):
    new_map = mapping.copy()
    a, b = random.sample("abcdefghijklmnopqrstuvwxyz", 2)

    for k in new_map:
        if new_map[k] == a:
            new_map[k] = b
        elif new_map[k] == b:
            new_map[k] = a

    return new_map


# ==========================================================
# MAIN SOLVER (SIMULATED ANNEALING)
# ==========================================================
def solve_substitution(ciphertext, iterations=40000):

    cipher = ciphertext.lower()

    best_map = seed_mapping(cipher)
    best_table = build_translate_table(best_map)
    best_plain = apply_mapping(cipher, best_table)
    best_score = score_text(best_plain)

    T = 4.0
    cooling = 0.9993

    for step in range(iterations):
        new_map = random_swap(best_map)
        new_table = build_translate_table(new_map)
        new_plain = apply_mapping(cipher, new_table)
        new_score = score_text(new_plain)

        if new_score > best_score:
            best_map = new_map
            best_score = new_score
            best_plain = new_plain
        else:
            prob = math.exp((new_score - best_score) / T)
            if random.random() < prob:
                best_map = new_map
                best_score = new_score
                best_plain = new_plain

        T *= cooling

    return best_score, best_map, best_plain


# ==========================================================
# DASHBOARD WRAPPER
# ==========================================================
def mono_decrypt(ciphertext):
    score, mapping, plaintext = solve_substitution(ciphertext)
    return score, mapping, plaintext
