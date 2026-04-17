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
# 1. CẤU HÌNH & CSS TÙY CHỈNH (GIAO DIỆN KHỐI)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

st.markdown("""
    <style>
    /* Tổng thể nền */
    .stApp { background-color: #f0f2f5; }
    
    /* Ô tiêu đề đỏ */
    .header-red {
        background-color: #d32f2f;
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Các nút chức năng xanh lá to, cân đối */
    div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        height: 120px !important; /* Tăng độ cao nút */
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #1b5e20 !important;
        transform: scale(1.02);
    }
    
    /* Ô đăng nhập */
    .login-container {
        border: 3px solid #d32f2f;
        padding: 40px;
        border-radius: 20px;
        background-color: white;
    }
    
    /* Ô nội dung bên trong */
    .content-box {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2e7d32;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
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
# 2. XỬ LÝ TRẠNG THÁI
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "home"

# ==========================================
# 3. MÀN HÌNH ĐĂNG NHẬP
# ==========================================
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("##")
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#d32f2f;'>🇻🇳 ĐĂNG NHẬP</h1>", unsafe_allow_html=True)
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("VÀO HỆ THỐNG"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. TRANG CHỦ (MENU CHÍNH)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="header-red"><h1>MENU CHÍNH - QUẢN TRỊ ĐẢNG VỤ</h1></div>', unsafe_allow_html=True)
    
    # Tạo 3 nút to cân đối
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("👤 HỒ SƠ\nĐẢNG VIÊN"):
            st.session_state.page = "hoso"
            st.rerun()
            
    with c2:
        if st.button("📤 LƯU VĂN BẢN\nMỚI"):
            st.session_state.page = "luu_vb"
            st.rerun()
            
    with c3:
        if st.button("🖼 KHO ẢNH\nVĂN BẢN"):
            st.session_state.page = "kho_anh"
            st.rerun()
            
    st.write("---")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- HÀM QUAY LẠI ---
def nut_quay_lai():
    if st.button("⬅️ QUAY LẠI MENU CHÍNH"):
        st.session_state.page = "home"
        st.rerun()

# ==========================================
# 5. CÁC TRANG CHỨC NĂNG
# ==========================================

# --- TRANG HỒ SƠ ---
if st.session_state.page == "hoso":
    st.markdown('<div class="header-red"><h2>👤 QUẢN LÝ HỒ SƠ ĐẢNG VIÊN</h2></div>', unsafe_allow_html=True)
    nut_quay_lai()
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    with st.form("f_hoso", clear_on_submit=True):
        t, c, g = st.text_input("Họ và tên"), st.text_input("Chức vụ"), st.text_area("Ghi chú")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if t:
                save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), t, c, g])
                st.success("Đã lưu!")
            else: st.warning("Hãy nhập họ tên.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📋 Danh sách Đảng viên")
    st.dataframe(load_data("HoSo"), use_container_width=True)

# --- TRANG LƯU VĂN BẢN ---
elif st.session_state.page == "luu_vb":
    st.markdown('<div class="header-red"><h2>📤 LƯU TRỮ VĂN BẢN MỚI</h2></div>', unsafe_allow_html=True)
    nut_quay_lai()
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    with st.form("f_vb", clear_on_submit=True):
        m1 = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m2 = st.selectbox("Loại văn bản:", ["Quyết định", "Công văn", "Kế hoạch", "Khác"]) if m1 == "Văn bản cấp trên" else m1
        ty = st.text_input("Trích yếu nội dung:")
        file = st.file_uploader("Chọn ảnh văn bản:", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if ty and file:
                img = Image.open(file).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=50)
                txt = base64.b64encode(buf.getvalue()).decode()
                if save_data("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M"), m1, m2, ty, txt]):
                    st.success("Lưu thành công!")
            else: st.warning("Điền đủ thông tin!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TRANG KHO ẢNH ---
elif st.session_state.page == "kho_anh":
    st.markdown('<div class="header-red"><h2>🖼 KHO VĂN BẢN ẢNH</h2></div>', unsafe_allow_html=True)
    nut_quay_lai()
    
    df = load_data("VanBan")
    if df.empty:
        st.info("Chưa có văn bản nào.")
    else:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Cấp trên", "Chi bộ", "Ảnh khác"])
        m_list = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        t_list = [tab1, tab2, tab3]
        
        for i, m in enumerate(m_list):
            with t_list[i]:
                sub_df = df[df.iloc[:, 1] == m]
                for idx, row in sub_df.iterrows():
                    with st.container():
                        col_txt, col_btn = st.columns([4, 1])
                        col_txt.markdown(f"**📄 {row.iloc[3]}**\n\n📅 {row.iloc[0]} | {row.iloc[2]}")
                        if col_btn.button("👁️ Xem", key=f"show_{idx}"):
                            st.session_state[f"view_{idx}"] = True
                        
                        if st.session_state.get(f"view_{idx}", False):
                            st.image(base64.b64decode(str(row.iloc[-1]).strip()), use_container_width=True)
                            if st.button("❌ Ẩn", key=f"hide_{idx}"):
                                st.session_state[f"view_{idx}"] = False
                                st.rerun()
                        st.write("---")
        st.markdown('</div>', unsafe_allow_html=True)
