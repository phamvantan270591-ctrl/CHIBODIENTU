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
# 1. CẤU HÌNH & CSS ĐẶC BIỆT CHO DI ĐỘNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

st.markdown("""
    <style>
    /* Ép các cột (columns) không được nhảy dòng trên điện thoại */
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 33% !important;
    }
    
    /* Căn chỉnh lại khoảng cách trên di động */
    .stApp { background-color: #f8f9fa; }
    
    .header-red {
        background-color: #d32f2f;
        color: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Thiết kế nút bấm hình vuông cân đối */
    div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        height: 110px !important; /* Giảm nhẹ độ cao để vừa màn hình điện thoại */
        width: 100% !important;
        font-size: 14px !important; /* Giảm font chữ để không bị tràn dòng */
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 5px !important;
    }

    div.stButton > button:hover {
        background-color: #1b5e20 !important;
    }
    
    /* Nút Đăng xuất màu xám */
    div.stButton > button[kind="secondary"] {
        background-color: #546e7a !important;
    }

    /* Ẩn các thành phần thừa của Streamlit để giống App hơn */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM HỖ TRỢ ---
def save_data(s_name, values):
    try:
        res = requests.post(SCRIPT_URL, data=json.dumps({"method": "append_row", "sheetName": s_name, "values": values}), timeout=30)
        return res.status_code == 200
    except: return False

def load_data(s_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={s_name}&t={int(time.time())}"
    try: return pd.read_csv(io.StringIO(requests.get(url).text), dtype=str).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. XỬ LÝ ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "home"

if not st.session_state.auth:
    _, col_login, _ = st.columns([0.1, 0.8, 0.1]) # Tối ưu độ rộng form login trên mobile
    with col_login:
        st.write("##")
        st.markdown('<div style="background-color:white; padding:20px; border-radius:15px; border:2px solid #d32f2f">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:#d32f2f;'>QUẢN TRỊ ĐẢNG VỤ</h3>", unsafe_allow_html=True)
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496": st.session_state.auth = True; st.rerun()
            else: st.error("Sai mật khẩu!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. MENU CHÍNH 6 KHỐI (DÀN HÀNG NGANG)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="header-red">DANH MỤC CHÍNH</div>', unsafe_allow_html=True)
    
    # Hàng 1: 3 cột nằm ngang
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤\nHỒ SƠ"): st.session_state.page = "hoso"; st.rerun()
    with c2:
        if st.button("📤\nLƯU VB"): st.session_state.page = "luu_vb"; st.rerun()
    with c3:
        if st.button("🖼\nKHO ẢNH"): st.session_state.page = "kho_anh"; st.rerun()

    # Hàng 2: 3 cột nằm ngang
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🚩\nHĐỘNG"): st.session_state.page = "hoat_dong"; st.rerun()
    with c5:
        if st.button("⏰\nNHẮC VIỆC"): st.session_state.page = "nhac_viec"; st.rerun()
    with c6:
        if st.button("🚪\nTHOÁT", type="secondary"): st.session_state.auth = False; st.rerun()

# --- NÚT QUAY LẠI ---
def back():
    if st.button("⬅️ MENU CHÍNH"):
        st.session_state.page = "home"; st.rerun()

# ==========================================
# 4. CÁC TRANG CHI TIẾT
# ==========================================
if st.session_state.page == "hoso":
    st.markdown('<div class="header-red">HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)
    back()
    with st.form("f1"):
        t, c = st.text_input("Họ tên"), st.text_input("Chức vụ")
        if st.form_submit_button("💾 LƯU"): 
            save_data("HoSo", [datetime.now().strftime("%d/%m/%Y"), t, c])
            st.success("Xong!")
    st.dataframe(load_data("HoSo"), use_container_width=True)

elif st.session_state.page == "luu_vb":
    st.markdown('<div class="header-red">LƯU VĂN BẢN</div>', unsafe_allow_html=True)
    back()
    with st.form("f2"):
        m1 = st.selectbox("Mục:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        ty = st.text_input("Trích yếu")
        f = st.file_uploader("Chọn ảnh", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 LƯU"):
            if ty and f:
                img = Image.open(f).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO(); img.save(buf, format="JPEG", quality=50)
                txt = base64.b64encode(buf.getvalue()).decode()
                save_data("VanBan", [datetime.now().strftime("%d/%m/%Y"), m1, m1, ty, txt])
                st.success("Đã lưu!")

elif st.session_state.page == "kho_anh":
    st.markdown('<div class="header-red">KHO VĂN BẢN</div>', unsafe_allow_html=True)
    back()
    df = load_data("VanBan")
    if not df.empty:
        for idx, row in df.iterrows():
            with st.expander(f"📄 {row.iloc[3]}"):
                st.image(base64.b64decode(str(row.iloc[-1]).strip()))
