# =============================
# tasks/des.py
# DES for Lab06 – ECB & CBC
# Compatible with app.py
# =============================

import os
from .des_tables import IP, FP, E, P, SBOX, PC1, PC2, SHIFTS


# ------------------------------
# Bit utilities
# ------------------------------
def bytes_to_bits(data: bytes):
    return [(byte >> (7 - i)) & 1 for byte in data for i in range(8)]


def bits_to_bytes(bits):
    return bytes([
        sum(bits[i*8 + j] << (7 - j) for j in range(8))
        for i in range(len(bits)//8)
    ])


def permute(block, table):
    return [block[i - 1] for i in table]


def xor(a, b):
    return [x ^ y for x, y in zip(a, b)]


def left_shift(bits, n):
    return bits[n:] + bits[:n]


# ------------------------------
# S-box substitution
# ------------------------------
def sbox_sub(bits48):
    out = []
    for box_id in range(8):
        block = bits48[box_id*6:(box_id+1)*6]
        row = (block[0] << 1) | block[5]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = SBOX[box_id][row][col]
        out += [(val >> (3 - i)) & 1 for i in range(4)]
    return out


# ------------------------------
# Feistel F-function
# ------------------------------
def F(right, subkey):
    expanded = permute(right, E)
    tmp = xor(expanded, subkey)
    s_out = sbox_sub(tmp)
    return permute(s_out, P)


# ------------------------------
# Key Schedule
# ------------------------------
def key_schedule(key64):
    key56 = permute(key64, PC1)
    C = key56[:28]
    D = key56[28:]

    subs = []
    for shift in SHIFTS:
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        subs.append(permute(C + D, PC2))
    return subs


# ------------------------------
# DES block encrypt / decrypt
# ------------------------------
def des_encrypt_block(bits64, subkeys):
    block = permute(bits64, IP)
    L, R = block[:32], block[32:]

    for i in range(16):
        L, R = R, xor(L, F(R, subkeys[i]))

    return permute(R + L, FP)


def des_decrypt_block(bits64, subkeys):
    block = permute(bits64, IP)
    L, R = block[:32], block[32:]

    for i in reversed(range(16)):
        L, R = R, xor(L, F(R, subkeys[i]))

    return permute(R + L, FP)


# ------------------------------
# PKCS7 Padding
# ------------------------------
def pkcs7_pad(data: bytes, block=8):
    pad_len = block - (len(data) % block)
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes):
    pad_len = data[-1]
    return data[:-pad_len]


# ------------------------------
# ECB Mode
# ------------------------------
def ECB_encrypt(plaintext: bytes, key: bytes):
    subkeys = key_schedule(bytes_to_bits(key))
    pt = pkcs7_pad(plaintext, 8)
    out = b""

    for i in range(0, len(pt), 8):
        block = bytes_to_bits(pt[i:i+8])
        enc_bits = des_encrypt_block(block, subkeys)
        out += bits_to_bytes(enc_bits)

    return out


def ECB_decrypt(cipher: bytes, key: bytes):
    subkeys = key_schedule(bytes_to_bits(key))
    out = b""

    for i in range(0, len(cipher), 8):
        block = bytes_to_bits(cipher[i:i+8])
        dec_bits = des_decrypt_block(block, subkeys)
        out += bits_to_bytes(dec_bits)

    return pkcs7_unpad(out)


# ------------------------------
# CBC Mode
# ------------------------------
def CBC_encrypt(plaintext: bytes, key: bytes, iv: bytes = None):
    if iv is None:
        iv = os.urandom(8)

    subkeys = key_schedule(bytes_to_bits(key))
    pt = pkcs7_pad(plaintext)
    prev = iv
    out = b""

    for i in range(0, len(pt), 8):
        block = pt[i:i+8]
        xored = bytes([a ^ b for a, b in zip(block, prev)])
        enc_bits = des_encrypt_block(bytes_to_bits(xored), subkeys)
        ct = bits_to_bytes(enc_bits)
        out += ct
        prev = ct

    return out, iv


def CBC_decrypt(cipher: bytes, key: bytes, iv: bytes):
    subkeys = key_schedule(bytes_to_bits(key))
    prev = iv
    out = b""

    for i in range(0, len(cipher), 8):
        block = cipher[i:i+8]
        dec_bits = des_decrypt_block(bytes_to_bits(block), subkeys)
        dec = bits_to_bytes(dec_bits)
        out += bytes([a ^ b for a, b in zip(dec, prev)])
        prev = block

    return pkcs7_unpad(out)


# ------------------------------
# PUBLIC API for app.py
# ------------------------------
def des_encrypt(plaintext: bytes, key: bytes, mode: str, iv=None):
    mode = mode.upper()

    if mode == "ECB":
        return ECB_encrypt(plaintext, key), None

    if mode == "CBC":
        ct, used_iv = CBC_encrypt(plaintext, key, iv)
        return ct, used_iv

    raise ValueError("Mode must be ECB or CBC")


def des_decrypt(ciphertext: bytes, key: bytes, mode: str, iv=None):
    mode = mode.upper()

    if mode == "ECB":
        return ECB_decrypt(ciphertext, key)

    if mode == "CBC":
        if iv is None:
            raise ValueError("CBC mode requires IV")
        return CBC_decrypt(ciphertext, key, iv)

    raise ValueError("Mode must be ECB or CBC")
