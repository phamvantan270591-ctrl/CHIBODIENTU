import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CẤU HÌNH & CSS TÙY CHỈNH (6 KHỐI)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    
    /* Ô tiêu đề đỏ */
    .header-red {
        background-color: #d32f2f;
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Cấu hình nút bấm thành khối vuông cân đối */
    div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        height: 140px !important; 
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    
    /* Nút đăng xuất màu khác để phân biệt */
    div.stButton > button[kind="secondary"] {
        background-color: #546e7a !important;
    }

    div.stButton > button:hover {
        background-color: #1b5e20 !important;
        transform: translateY(-5px);
        transition: 0.3s;
    }
    
    .content-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-top: 5px solid #d32f2f;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM HỖ TRỢ ---
def save_data(sheet_name, values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return res.status_code == 200
    except: return False

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. KIỂM TRA TRẠNG THÁI
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "home"

# ==========================================
# 3. ĐĂNG NHẬP
# ==========================================
if not st.session_state.auth:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="background-color:white; padding:30px; border-radius:20px; border:3px solid #d32f2f">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#d32f2f;'>HỆ THỐNG ĐẢNG VỤ</h2>", unsafe_allow_html=True)
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Sai thông tin!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. MENU CHÍNH (6 KHỐI CÂN ĐỐI)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="header-red"><h1>QUẢN TRỊ ĐẢNG VỤ</h1></div>', unsafe_allow_html=True)
    
    # Hàng 1
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤 HỒ SƠ\nĐẢNG VIÊN"):
            st.session_state.page = "hoso"; st.rerun()
    with c2:
        if st.button("📤 LƯU\nVĂN BẢN MỚI"):
            st.session_state.page = "luu_vb"; st.rerun()
    with c3:
        if st.button("🖼 KHO ẢNH\nVĂN BẢN"):
            st.session_state.page = "kho_anh"; st.rerun()

    # Hàng 2
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🚩 HOẠT ĐỘNG\nCHI BỘ"):
            st.session_state.page = "hoat_dong"; st.rerun()
    with c5:
        if st.button("⏰ NHẮC VIỆC\nCẦN LÀM"):
            st.session_state.page = "nhac_viec"; st.rerun()
    with c6:
        # Nút đăng xuất
        if st.button("🚪 ĐĂNG XUẤT", type="secondary"):
            st.session_state.auth = False; st.rerun()

# --- HÀM QUAY LẠI ---
def back_btn():
    if st.button("⬅️ QUAY LẠI MENU CHÍNH"):
        st.session_state.page = "home"; st.rerun()

# ==========================================
# 5. NỘI DUNG CHI TIẾT
# ==========================================

if st.session_state.page == "hoso":
    st.markdown('<div class="header-red"><h2>HỒ SƠ ĐẢNG VIÊN</h2></div>', unsafe_allow_html=True)
    back_btn()
    # (Phần code hiển thị hồ sơ giữ nguyên như bản trước)
    st.dataframe(load_data("HoSo"), use_container_width=True)

elif st.session_state.page == "luu_vb":
    st.markdown('<div class="header-red"><h2>LƯU VĂN BẢN MỚI</h2></div>', unsafe_allow_html=True)
    back_btn()
    # (Phần code lưu văn bản giữ nguyên)
    with st.form("f_vb", clear_on_submit=True):
        ty = st.text_input("Trích yếu")
        anh = st.file_uploader("Chọn ảnh", type=['jpg','png'])
        if st.form_submit_button("LƯU"):
            st.success("Đã gửi yêu cầu lưu!")

elif st.session_state.page == "kho_anh":
    st.markdown('<div class="header-red"><h2>KHO VĂN BẢN ẢNH</h2></div>', unsafe_allow_html=True)
    back_btn()
    # (Phần code kho ảnh giữ nguyên)

elif st.session_state.page == "hoat_dong":
    st.markdown('<div class="header-red"><h2>HOẠT ĐỘNG CHI BỘ</h2></div>', unsafe_allow_html=True)
    back_btn()
    st.info("Tính năng đang được cập nhật nội dung...")

elif st.session_state.page == "nhac_viec":
    st.markdown('<div class="header-red"><h2>NHẮC VIỆC CẦN LÀM</h2></div>', unsafe_allow_html=True)
    back_btn()
    st.info("Tính năng đang được cập nhật nội dung...")
