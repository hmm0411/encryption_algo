import streamlit as st
from streamlit_option_menu import option_menu
import json
from tasks.caesar import caesar_bruteforce
from tasks.mono import mono_decrypt
from tasks.vigenere import vigenere_auto_decrypt
from tasks.des import des_encrypt, des_decrypt
from tasks.aes import aes_encrypt, aes_decrypt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Lab06 Encryption Dashboard",
    layout="wide"
)

# ---------------- THEME CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e9f2ff 0%, #f7faff 80%);
}
.main > div {
    background: rgba(255, 255, 255, 0.65);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #dce7f7;
}
.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #1c4d8c;
    margin-bottom: 10px;
    margin-top: 10px;
}
.stButton > button {
    background: linear-gradient(90deg, #2d74da, #3c8df2);
    color: white;
    font-weight: bold;
    padding: 10px 18px;
    border-radius: 8px;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #1f5bbd, #2d74da);
}
input, textarea {
    background: #ffffff !important;
    border: 1px solid #c9d7ee !important;
    border-radius: 8px !important;
    color: #24416b !important;
}
section[data-testid="stSidebar"] {
    background: #f0f5ff !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style="display:flex; align-items:center; gap:15px; padding-bottom:10px;">
    <img src="https://www.uit.edu.vn/sites/vi/files/images/Logos/Logo_UIT_Web_Transparent.png"
         style="width:80px;">
    <div>
        <h1 style="margin:0; color:#1c4d8c; font-weight:800;">Lab06 – Encryption Algorithms</h1>
        <p style="margin:0; color:#46638f; font-size:17px;">Nguyễn Lê Hạ My - 23520964</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR MENU ----------------
with st.sidebar:
    st.markdown("## MENU")

    selected = option_menu(
        "",
        ["Task 1 - Caesar",
         "Task 2 - Monoalphabetic",
         "Task 3 - Vigenère",
         "Task 4 - DES",
         "Task 5 - AES"],
        icons=["1-circle", "2-circle", "3-circle", "4-circle", "5-circle"],
        default_index=0
    )

def loading(msg="Đang xử lý…"):
    with st.spinner(msg):
        import time
        time.sleep(0.8)

# TASK 1 — CAESAR
if selected == "Task 1 - Caesar":

    st.markdown("<div class='section-title'>Task 1 – Caesar Cipher (Bruteforce Decode)</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Tải file ciphertext (.txt)", type=["txt"], key="caesar_file")  

    ciphertext = ""
    if uploaded:
        ciphertext = uploaded.read().decode("utf-8")
        st.success("Đã tải ciphertext thành công!")
        st.write(f"Độ dài văn bản: **{len(ciphertext)} ký tự**")

    if st.button("Giải mã (Bruteforce)", key="caesar_btn"):  
        if ciphertext.strip() == "":
            st.warning("Vui lòng import file ciphertext trước!")
        else:
            with st.spinner("Đang thử tất cả 26 khóa..."):
                key, plaintext = caesar_bruteforce(ciphertext)
            st.session_state["caesar_key"] = key
            st.session_state["caesar_plain"] = plaintext
            st.success(f"Khóa tìm được: **{key}**")

    key = st.session_state.get("caesar_key", None)
    plaintext = st.session_state.get("caesar_plain", "")

    if key is not None:
        st.text_area("Input:", value=ciphertext, height=350, key="caesar_input")   
        export_text = str(key) + "\n" + plaintext

        st.text_area("Output:", value=export_text, height=350, key="caesar_output")  

        st.download_button(
            label="Tải file plaintext.txt",
            data=export_text,
            file_name="plaintext_output.txt",
            mime="text/plain",
            key="caesar_dl"  
        )


# TASK 2 — MONOALPHABETIC
elif selected == "Task 2 - Monoalphabetic":

    st.markdown("<div class='section-title'>Task 2 - Mono-alphabetic Cipher</div>", unsafe_allow_html=True)

    file = st.file_uploader("Upload ciphertext (.txt)", type=["txt"], key="mono_file") 

    if file:
        ct = file.read().decode("utf-8")

        with st.spinner("Đang giải mã bằng Simulated Annealing…"):
            score, mapping, plaintext = mono_decrypt(ct)

        st.success("Giải mã thành công!")
        st.text_area("Input:", value=ct, height=350, key="mono_input")
        st.text_area("Score:", value=str(score), key="mono_score")
        st.text_area("Mapping:", value=json.dumps(mapping, indent=4), height=250, key="mono_map")

        output_text = str(score) + "\n" + str(mapping) + "\n" + plaintext
        st.text_area("Output:", output_text, height=350, key="mono_output")  

        st.download_button(
            label="Tải file plaintext",
            data=output_text,
            file_name="mono_output.txt",
            mime="text/plain",
            key="mono_dl"  
        )


# TASK 3 — VIGENERE
elif selected == "Task 3 - Vigenère":

    st.markdown("<div class='section-title'>Task 3 - Vigenère Cipher</div>", unsafe_allow_html=True)

    file = st.file_uploader("Upload ciphertext (.txt)", type=["txt"], key="vig_file")  

    if file:
        ct = file.read().decode("utf-8")

        with st.spinner("Đang giải mã bằng Kasiski + IC + Chi-square…"):
            key, pt = vigenere_auto_decrypt(ct)

        st.success(f"Khóa tìm được: {key}")

        output_text = key + "\n" + pt

        st.text_area("Input:", value=ct, height=350, key="vig_input") 
        st.text_area("Output:", output_text, height=350, key="vig_output")  

        st.download_button(
            label="Tải file plaintext",
            data=output_text,
            file_name="vigenere_output.txt",
            mime="text/plain",
            key="vig_dl"  
        )

# TASK 4 — DES
elif selected == "Task 4 - DES":

    st.markdown("<div class='section-title'>Task 4 - DES</div>", unsafe_allow_html=True)

    mode = st.selectbox("Mode DES:", ["ECB", "CBC"], key="des_mode")
    key_hex = st.text_input("Key (16 hex)", "133457799BBCDFF1", key="des_key")

    col1, col2 = st.columns(2)

    # ---------------------- ENCRYPT ----------------------
    with col1:
        st.subheader("Mã hóa")
        pt = st.text_area("Plaintext:", key="des_plaintext_input")

        if st.button("Mã hóa DES", key="des_encrypt_btn"):
            loading("Đang mã hóa...")
            key = bytes.fromhex(key_hex)

            ct, iv = des_encrypt(pt.encode(), key, mode)

            st.write("Ciphertext (hex):")
            st.code(ct.hex())

            # SAVE SESSION
            st.session_state["des_ct"] = ct.hex()

            if iv:
                st.write("IV (hex):")
                st.code(iv.hex())
                st.session_state["des_iv"] = iv.hex()

    # ---------------------- DECRYPT ----------------------
    with col2:
        st.subheader("Giải mã")

        ct_hex = st.text_input("Ciphertext hex", value=st.session_state.get("des_ct", ""), key="des_ct_hex")
        iv_hex = st.text_input("IV hex (CBC only)", value=st.session_state.get("des_iv", ""), key="des_iv_hex")

        # Always keep IV in session
        st.session_state["des_iv"] = iv_hex

        if st.button("Giải mã DES", key="des_decrypt_btn"):

            if mode == "CBC" and iv_hex.strip() == "":
                st.error("CBC mode yêu cầu nhập IV!")
            else:
                loading("Đang giải mã...")

                key = bytes.fromhex(key_hex)
                ct = bytes.fromhex(ct_hex)
                iv = bytes.fromhex(iv_hex) if iv_hex else None

                out = des_decrypt(ct, key, mode, iv)

                st.text_area("Plaintext:", out.decode(errors="ignore"), key="des_plaintext_output")

# TASK 5 — AES
elif selected == "Task 5 - AES":

    st.markdown("<div class='section-title'>Task 5 - AES</div>", unsafe_allow_html=True)

    mode = st.selectbox("Mode AES:", ["ECB", "CBC"], key="aes_mode")
    key_hex = st.text_input("Key (32 hex)", "00112233445566778899AABBCCDDEEFF", key="aes_key")

    col1, col2 = st.columns(2)

    # ---------------------- ENCRYPT ----------------------
    with col1:
        st.subheader("Mã hóa")
        pt = st.text_area("Plaintext:", key="aes_plaintext_input")

        if st.button("Mã hóa AES", key="aes_encrypt_btn"):
            loading("Đang mã hóa...")

            key = bytes.fromhex(key_hex)

            ct_hex, iv = aes_encrypt(pt.encode(), key, mode)

            st.write("Ciphertext (hex):")
            st.code(ct_hex)
            st.session_state["aes_ct"] = ct_hex

            if iv:
                st.write("IV (hex):")
                st.code(iv.hex())
                st.session_state["aes_iv"] = iv.hex()

    # ---------------------- DECRYPT ----------------------
    with col2:
        st.subheader("Giải mã")

        ct_hex = st.text_input("Ciphertext hex", value=st.session_state.get("aes_ct", ""), key="aes_ct_input")
        iv_hex = st.text_input("IV hex (CBC only)", value=st.session_state.get("aes_iv", ""), key="aes_iv_input")

        st.session_state["aes_iv"] = iv_hex

        if st.button("Giải mã AES", key="aes_decrypt_btn"):

            if mode == "CBC" and iv_hex.strip() == "":
                st.error("CBC mode yêu cầu nhập IV!")
            else:
                loading("Đang giải mã...")

                key = bytes.fromhex(key_hex)
                iv = bytes.fromhex(iv_hex) if iv_hex else None

                pt_bytes = aes_decrypt(ct_hex, key, mode, iv)

                st.text_area("Plaintext:", pt_bytes.decode(errors="ignore"), key="aes_plaintext_output")

