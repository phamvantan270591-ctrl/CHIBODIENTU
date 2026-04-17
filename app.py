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
# 1. CẤU HÌNH & CSS (GIAO DIỆN XANH LÁ)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

st.markdown("""
    <style>
    /* Nút bấm xanh lá kiểu hình chữ nhật */
    div.stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        height: 80px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        background-color: #218838 !important;
        border: 2px solid #fff !important;
    }
    /* Chỉnh màu chữ đăng nhập */
    .login-box {
        border: 2px solid #28a745;
        padding: 30px;
        border-radius: 15px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM XỬ LÝ ---
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
# 2. XỬ LÝ TRẠNG THÁI (SESSION STATE)
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "home"

# ==========================================
# 3. TRANG ĐĂNG NHẬP
# ==========================================
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("#")
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#28a745;'>HỆ THỐNG ĐẢNG VỤ</h2>", unsafe_allow_html=True)
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Thông tin không chính xác!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. TRANG CHỦ (SAU KHI ĐĂNG NHẬP - 3 NÚT XANH)
# ==========================================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>MENU CHÍNH</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col_a, col_b, col_c = st.columns([1, 1, 1])
    
    if col_a.button("👤 HỒ SƠ\nĐẢNG VIÊN"):
        st.session_state.page = "hoso"
        st.rerun()
        
    if col_b.button("📤 LƯU\nVĂN BẢN MỚI"):
        st.session_state.page = "luu_vb"
        st.rerun()
        
    if col_c.button("🖼 KHO ẢNH\nVĂN BẢN"):
        st.session_state.page = "kho_anh"
        st.rerun()
        
    st.write("#")
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- NÚT QUAY LẠI CHUNG ---
def quay_lai():
    if st.button("⬅️ Quay lại Menu chính"):
        st.session_state.page = "home"
        st.rerun()

# ==========================================
# 5. CÁC TRANG NỘI DUNG
# ==========================================

# --- TRANG HỒ SƠ ---
if st.session_state.page == "hoso":
    st.header("👤 HỒ SƠ ĐẢNG VIÊN")
    quay_lai()
    with st.form("f_hoso", clear_on_submit=True):
        ten = st.text_input("Họ tên")
        cv = st.text_input("Chức vụ")
        gc = st.text_area("Ghi chú")
        if st.form_submit_button("💾 LƯU"):
            if ten:
                save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc])
                st.success("Đã lưu!")
    st.dataframe(load_data("HoSo"), use_container_width=True)

# --- TRANG LƯU VĂN BẢN ---
elif st.session_state.page == "luu_vb":
    st.header("📤 LƯU VĂN BẢN MỚI")
    quay_lai()
    with st.form("f_vb", clear_on_submit=True):
        m1 = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m2 = st.selectbox("Loại:", ["Quyết định", "Công văn", "Kế hoạch", "Khác"]) if m1 == "Văn bản cấp trên" else m1
        ty = st.text_input("Trích yếu nội dung:")
        anh = st.file_uploader("Chọn ảnh:", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if ty and anh:
                img = Image.open(anh).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=50)
                txt = base64.b64encode(buf.getvalue()).decode()
                if save_data("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M"), m1, m2, ty, txt]):
                    st.success("Đã lưu thành công!")
            else: st.warning("Điền đủ thông tin!")

# --- TRANG KHO ẢNH ---
elif st.session_state.page == "kho_anh":
    st.header("🖼 KHO VĂN BẢN ẢNH")
    quay_lai()
    df = load_data("VanBan")
    if df.empty:
        st.info("Chưa có dữ liệu.")
    else:
        tab1, tab2, tab3 = st.tabs(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m_list = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        t_list = [tab1, tab2, tab3]
        
        for i, m in enumerate(m_list):
            with t_list[i]:
                sub_df = df[df.iloc[:, 1] == m]
                for idx, row in sub_df.iterrows():
                    with st.container():
                        c1, c2 = st.columns([4, 1])
                        c1.markdown(f"**📄 {row.iloc[3]}**\n\n📅 {row.iloc[0]} | Loại: {row.iloc[2]}")
                        if c2.button("👁️ Xem", key=f"v_{idx}"):
                            st.session_state[f"img_{idx}"] = True
                        
                        if st.session_state.get(f"img_{idx}", False):
                            st.image(base64.b64decode(str(row.iloc[-1]).strip()), use_container_width=True)
                            if st.button("❌ Ẩn", key=f"h_{idx}"):
                                st.session_state[f"img_{idx}"] = False
                                st.rerun()
                        st.write("---")
