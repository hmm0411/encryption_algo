def shift_char(c, k):
    """
    Dịch NGƯỢC ký tự (giải mã).
    Chỉ dịch A–Z, a–z.
    Các ký tự khác: giữ nguyên theo yêu cầu đề bài.
    """
    if 'a' <= c <= 'z':
        return chr((ord(c) - ord('a') - k) % 26 + ord('a'))
    elif 'A' <= c <= 'Z':
        return chr((ord(c) - ord('A') - k) % 26 + ord('A'))
    else:
        return c


def score_text(text):
    """
    Chấm điểm độ “giống tiếng Anh”.
    Cách đơn giản và hiệu quả cho văn bản > 5000 từ:
        - Space (từ xuất hiện nhiều)
        - 'e' (chữ phổ biến nhất)
    """
    return text.count(" ") * 2 + text.count("e") + text.count("E")


def decrypt_with_key(ciphertext, k):
    """Giải mã với 1 khóa k."""
    return "".join(shift_char(c, k) for c in ciphertext)


def caesar_bruteforce(ciphertext):
    """
    Thử tất cả khóa k = 0..25
    Trả về:
        best_key, best_plaintext
    """
    best_score = -1
    best_key = 0
    best_plaintext = ""

    for k in range(26):
        plain = decrypt_with_key(ciphertext, k)
        s = score_text(plain)

        if s > best_score:
            best_score = s
            best_key = k
            best_plaintext = plain

    return best_key, best_plaintext


# CHƯƠNG TRÌNH CHẠY ĐỘC LẬP (FILE I/O)
def main():
    input_file = "ciphertext.txt"
    output_file = "plaintext.txt"

    # ĐỌC FILE INPUT
    with open(input_file, "r", encoding="utf-8") as f:
        ciphertext = f.read()

    # GIẢI MÃ CAESAR 
    key, plaintext = caesar_bruteforce(ciphertext)

    # GHI FILE OUTPUT 
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(key) + "\n")     # dòng 1 = khóa
        f.write(plaintext)           # dòng 2 = plaintext

    print("Done! Output saved to:", output_file)
    print("Best key =", key)


if __name__ == "__main__":
    main()
