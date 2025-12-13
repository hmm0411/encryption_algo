from tasks.aes_core import (
    sub_bytes, inv_sub_bytes,
    shift_rows, inv_shift_rows,
    mix_columns, inv_mix_columns,
    add_round_key
)

#  Hàm chuyển đổi giữa bytes <-> state matrix (4×4)
def bytes_to_state(block16: bytes):
    """
    Chuyển 16 byte thành state matrix 4×4 theo chuẩn AES.
    
    block16 = b0 b1 b2 ... b15
    state[r][c] = b[r + 4*c]
    
    cột 0: b0 b1 b2 b3
    cột 1: b4 b5 b6 b7
    cột 2: b8 b9 b10 b11
    cột 3: b12 b13 b14 b15
    """
    return [
        [block16[0], block16[4], block16[8],  block16[12]],
        [block16[1], block16[5], block16[9],  block16[13]],
        [block16[2], block16[6], block16[10], block16[14]],
        [block16[3], block16[7], block16[11], block16[15]],
    ]


def state_to_bytes(state):
    """
    Chuyển state 4×4 về bytes theo chuẩn AES.
    """
    return bytes([
        state[0][0], state[1][0], state[2][0], state[3][0],
        state[0][1], state[1][1], state[2][1], state[3][1],
        state[0][2], state[1][2], state[2][2], state[3][2],
        state[0][3], state[1][3], state[2][3], state[3][3],
    ])


#  AES Encrypt 1 block (16 byte)
def aes_encrypt_block(block16: bytes, round_keys):
    """
    Mã hóa AES 1 block (16 byte):
      - round_keys là list các round key từ key_expansion()
      - Nr = len(round_keys) - 1

    Quy trình:
      state = AddRoundKey
      for round = 1..Nr-1:
           SubBytes
           ShiftRows
           MixColumns
           AddRoundKey
      round cuối:
           SubBytes
           ShiftRows
           AddRoundKey
    """
    state = bytes_to_state(block16)
    Nr = len(round_keys) - 1

    # Round 0
    state = add_round_key(state, round_keys[0])

    # Round 1...Nr-1
    for rnd in range(1, Nr):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[rnd])

    # Round Nr
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[Nr])

    return state_to_bytes(state)


#  AES Decrypt 1 block (16 byte)
def aes_decrypt_block(block16: bytes, round_keys):
    """
    Giải mã AES 1 block (16 byte)
    round_keys được đưa vào theo thứ tự từ key_expansion().
    """
    state = bytes_to_state(block16)
    Nr = len(round_keys) - 1

    # Round 0 (vòng cuối của mã hóa)
    state = add_round_key(state, round_keys[Nr])

    # Round Nr-1 ... 1
    for rnd in range(Nr - 1, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, round_keys[rnd])
        state = inv_mix_columns(state)

    # Round 0
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, round_keys[0])

    return state_to_bytes(state)
