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
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

# Giao diện
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;
    }
    .feature-card {
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #d32f2f; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HÀM XỬ LÝ DỮ LIỆU
# ==========================================
def save_to_sheets(sheet_name, row_values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": row_values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=60)
        return res.status_code == 200
    except: return False

def get_data_fresh(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        df = pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
        return df
    except: return pd.DataFrame()

def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((800, 800)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60, optimize=True)
    return buffer.getvalue()

# ==========================================
# 3. ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown('<div class="feature-card" style="text-align:center; margin-top:50px;">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=70)
        st.subheader("HỆ THỐNG QUẢN TRỊ")
        with st.form("login"):
            u = st.text_input("Tên đăng nhập:")
            p = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("ĐĂNG NHẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Sai thông tin!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>DANH MỤC</h2>", unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản mới", "🖼 Xem kho văn bản ảnh"])
    if st.button("🚪 Đăng xuất"):
        st.session
