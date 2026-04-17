import streamlit as st
import pandas as pd

# 1. GIAO DIỆN
st.set_page_config(page_title="QUẢN TRỊ CHI BỘ", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; }
    .title-viet { color: #cc0000; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. ĐĂNG NHẬP
if 'login' not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.markdown("<h2 class='title-viet'>🇻🇳 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    user = st.text_input("Tên đăng nhập:")
    pwd = st.text_input("Mật khẩu:", type="password")
    if st.button("VÀO PHẦN MỀM"):
        if user == "Admin" and pwd == "Tan@753496":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# 3. NỘI DUNG SAU ĐĂNG NHẬP
st.markdown("<h1 class='title-viet'>QUẢN TRỊ ĐẢNG VỤ CÁ NHÂN</h1>", unsafe_allow_html=True)

menu = st.tabs(["🔍 TÌM KIẾM", "👤 ĐẢNG VIÊN", "📂 VĂN BẢN"])

with menu[0]:
    st.subheader("🔎 Tra cứu nhanh")
    search = st.text_input("Nhập tên hoặc từ khóa cần tìm...")
    st.write("Kết quả sẽ hiển thị tại đây...")

with menu[1]:
    st.subheader("🗂 Danh sách Đảng viên")
    # Giả lập dữ liệu để không bị lỗi đỏ
    data = {"Họ tên": ["Nguyễn Văn A", "Trần Thị B"], "Chức vụ": ["Bí thư", "Phó Bí thư"]}
    st.table(pd.DataFrame(data))

with menu[2]:
    st.subheader("📸 Kho ảnh văn bản")
    st.file_uploader("Bấm để chụp ảnh văn bản/công văn:", type=['jpg', 'png'])
    st.button("LƯU TRỮ")
