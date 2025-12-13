from tasks.aes_tables import SBOX, INV_SBOX, xtime

# SubBytes & InvSubBytes
def sub_bytes(state):
    """
    Áp dụng SBOX lên toàn bộ 4x4 byte trong state.
    state[r][c] là 1 byte.
    """
    for r in range(4):
        for c in range(4):
            state[r][c] = SBOX[state[r][c]]
    return state


def inv_sub_bytes(state):
    """
    Áp dụng INV_SBOX (giải mã)
    """
    for r in range(4):
        for c in range(4):
            state[r][c] = INV_SBOX[state[r][c]]
    return state

# ShiftRows & InvShiftRows
def shift_rows(state):
    """
    Dịch vòng trái mỗi hàng:
    row 0: 0
    row 1: 1
    row 2: 2
    row 3: 3
    """
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]
    return state


def inv_shift_rows(state):
    """
    Dịch vòng phải để đảo lại ShiftRows
    """
    state[1] = state[1][-1:] + state[1][:-1]
    state[2] = state[2][-2:] + state[2][:-2]
    state[3] = state[3][-3:] + state[3][:-3]
    return state


# MixColumns & InvMixColumns
def mix_single_column(col):
    """
    MixColumns cho 1 cột (4 byte)
    Công thức MixColumns trong GF(2^8)
    """
    t = col[0] ^ col[1] ^ col[2] ^ col[3]
    u = col[0]
    col[0] ^= t ^ xtime(col[0] ^ col[1])
    col[1] ^= t ^ xtime(col[1] ^ col[2])
    col[2] ^= t ^ xtime(col[2] ^ col[3])
    col[3] ^= t ^ xtime(col[3] ^ u)
    return col


def mix_columns(state):
    """
    MixColumns cho toàn bộ state 4x4
    """
    for c in range(4):
        col = [state[r][c] for r in range(4)]
        col = mix_single_column(col)
        for r in range(4):
            state[r][c] = col[r]
    return state


# --- Inverse MixColumns -------------------------------

def gf_mul(a, b):
    """
    Nhân trong trường GF(2^8)
    """
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def inv_mix_single_column(col):
    """
    Phép MixColumns đảo (Inverse MixColumns)
    """
    a0, a1, a2, a3 = col
    col[0] = gf_mul(a0, 0x0e) ^ gf_mul(a1, 0x0b) ^ gf_mul(a2, 0x0d) ^ gf_mul(a3, 0x09)
    col[1] = gf_mul(a0, 0x09) ^ gf_mul(a1, 0x0e) ^ gf_mul(a2, 0x0b) ^ gf_mul(a3, 0x0d)
    col[2] = gf_mul(a0, 0x0d) ^ gf_mul(a1, 0x09) ^ gf_mul(a2, 0x0e) ^ gf_mul(a3, 0x0b)
    col[3] = gf_mul(a0, 0x0b) ^ gf_mul(a1, 0x0d) ^ gf_mul(a2, 0x09) ^ gf_mul(a3, 0x0e)
    return col


def inv_mix_columns(state):
    """
    Áp dụng inverse MixColumns cho 4 cột
    """
    for c in range(4):
        col = [state[r][c] for r in range(4)]
        col = inv_mix_single_column(col)
        for r in range(4):
            state[r][c] = col[r]
    return state

# AddRoundKey
def add_round_key(state, round_key):
    """
    XOR state với round_key.
    round_key[r][c] = byte.
    """
    for r in range(4):
        for c in range(4):
            state[r][c] ^= round_key[r][c]
    return state
