from tasks.aes_modes import (
    aes_ecb_encrypt,
    aes_ecb_decrypt,
    aes_cbc_encrypt,
    aes_cbc_decrypt
)

#  AES ENCRYPT
def aes_encrypt(plaintext: bytes, key: bytes, mode: str, iv=None):
    """
    plaintext: bytes
    key: 16 / 24 / 32 bytes
    mode: 'ECB' hoặc 'CBC'
    iv: 16 bytes hoặc None

    Output:
        - ciphertext dạng HEX (string)
        - iv (bytes hoặc None)
    """
    mode = mode.upper()

    if mode == "ECB":
        ct = aes_ecb_encrypt(plaintext, key)
        return ct.hex(), None

    elif mode == "CBC":
        ct, used_iv = aes_cbc_encrypt(plaintext, key, iv)
        return ct.hex(), used_iv

    else:
        raise ValueError("AES mode must be ECB or CBC")

#  AES DECRYPT
def aes_decrypt(ciphertext_hex: str, key: bytes, mode: str, iv=None):
    """
    ciphertext_hex: chuỗi hex
    key: bytes
    mode: 'ECB' hoặc 'CBC'
    iv: bytes (CBC bắt buộc)

    Trả về:
        plaintext (bytes)
    """
    mode = mode.upper()
    ciphertext = bytes.fromhex(ciphertext_hex)

    if mode == "ECB":
        return aes_ecb_decrypt(ciphertext, key)

    elif mode == "CBC":
        if iv is None:
            raise ValueError("IV is required for CBC decryption")
        return aes_cbc_decrypt(ciphertext, key, iv)

    else:
        raise ValueError("AES mode must be ECB or CBC")
