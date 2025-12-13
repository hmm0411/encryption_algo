import os
from tasks.aes_block import aes_encrypt_block, aes_decrypt_block
from tasks.aes_key_expansion import key_expansion

# Padding PKCS#7
def pkcs7_pad(data: bytes, block_size=16) -> bytes:
    pad = block_size - (len(data) % block_size)
    return data + bytes([pad]) * pad


def pkcs7_unpad(data: bytes) -> bytes:
    pad = data[-1]
    return data[:-pad]

# MODE ECB
def aes_ecb_encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    AES ECB mode – mã hóa
    plaintext: bytes
    key: 16/24/32 byte
    """
    round_keys = key_expansion(key)
    padded = pkcs7_pad(plaintext, 16)

    ciphertext = b""
    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        ciphertext += aes_encrypt_block(block, round_keys)

    return ciphertext


def aes_ecb_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    AES ECB mode – giải mã
    """
    round_keys = key_expansion(key)

    plaintext = b""
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        plaintext += aes_decrypt_block(block, round_keys)

    return pkcs7_unpad(plaintext)


# MODE CBC
def aes_cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes = None):
    """
    AES CBC mode – mã hóa
    Nếu IV không cung cấp -> tự sinh IV ngẫu nhiên 16 byte.
    Trả về (ciphertext, iv)
    """
    if iv is None:
        iv = os.urandom(16)

    round_keys = key_expansion(key)
    padded = pkcs7_pad(plaintext, 16)

    ciphertext = b""
    prev = iv

    for i in range(0, len(padded), 16):
        block = padded[i:i+16]
        x = bytes([a ^ b for a, b in zip(block, prev)])
        c = aes_encrypt_block(x, round_keys)
        ciphertext += c
        prev = c

    return ciphertext, iv


def aes_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    AES CBC mode – giải mã
    """
    round_keys = key_expansion(key)

    plaintext = b""
    prev = iv

    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        dec = aes_decrypt_block(block, round_keys)
        plaintext += bytes([a ^ b for a, b in zip(dec, prev)])
        prev = block

    return pkcs7_unpad(plaintext)
