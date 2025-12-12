# ============================================
# aes_key_expansion.py
# ============================================
# Phụ thuộc: aes_tables.py (SBOX, RCON)
# Hỗ trợ AES-128 (16 byte), AES-192 (24 byte), AES-256 (32 byte)

from tasks.aes_tables import SBOX, RCON

# -------------------------------------------------
# Các hàm xử lý Word cho Key Expansion
# -------------------------------------------------

def sub_word(word):
    """
    Áp dụng SBOX lên 4 byte trong một word.
    word = list gồm 4 byte [w0, w1, w2, w3]
    """
    return [SBOX[b] for b in word]


def rot_word(word):
    """
    Dịch vòng trái 1 byte:
    [a0, a1, a2, a3] -> [a1, a2, a3, a0]
    """
    return word[1:] + word[:1]


# -------------------------------------------------
# KEY EXPANSION (HỖ TRỢ 128/192/256-bit)
# -------------------------------------------------

def key_expansion(key_bytes):
    """
    Hàm mở rộng khóa AES theo chuẩn FIPS-197.

    key_bytes: bytes của khóa (16, 24, hoặc 32 byte)
    Trả về: danh sách round keys, mỗi round key kích thước 4x4 byte (state matrix)

    Số vòng (Nr):
        AES-128 => 10
        AES-192 => 12
        AES-256 => 14
    """

    key_len = len(key_bytes)
    if key_len not in (16, 24, 32):
        raise ValueError("AES key must be 128/192/256 bits (16/24/32 bytes).")

    Nk = key_len // 4                 # số word trong khóa gốc
    Nr = {16:10, 24:12, 32:14}[key_len]  # số vòng

    # Convert key to list of 4-byte words
    key_schedule = []
    for i in range(Nk):
        word = list(key_bytes[4*i : 4*(i+1)])
        key_schedule.append(word)

    # Tổng số word cần sinh
    total_words = 4 * (Nr + 1)

    i = Nk
    while i < total_words:
        temp = key_schedule[i - 1].copy()

        if i % Nk == 0:
            # RotWord + SubWord + Rcon
            temp = rot_word(temp)
            temp = sub_word(temp)
            temp[0] ^= RCON[i // Nk]

        elif Nk == 8 and (i % Nk == 4):
            # AES-256 yêu cầu SubWord thêm ở word thứ 4
            temp = sub_word(temp)

        # Word mới = word cách Nk vị trí XOR temp
        new_word = [key_schedule[i - Nk][j] ^ temp[j] for j in range(4)]
        key_schedule.append(new_word)

        i += 1

    # -----------------------------------------------------------
    # Chuyển về dạng round key: mỗi round key có 4 word (16 byte)
    # round_keys[round][column][row]
    # -----------------------------------------------------------

    round_keys = []
    for r in range(Nr + 1):
        rk_words = key_schedule[4*r : 4*(r+1)]   # 4 word

        # Convert word -> state matrix (4x4)
        # Trật tự state AES: cột → dòng
        state = [
            [rk_words[c][r] for c in range(4)]  # row r
            for r in range(4)
        ]
        # Note: state[r][c] = rk_words[c][r]

        round_keys.append(state)

    return round_keys
