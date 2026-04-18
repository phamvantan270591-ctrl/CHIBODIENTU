import streamlit as st
import pandas as pd
import requests
import io
import time
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH 
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="QUẢN TRỊ NỘI BỘ", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN KHỐI CHỮ NHẬT CAO CẤP (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Nền ứng dụng xám nhạt cao cấp */
    .stApp { background-color: #f4f7f9; }
    
    /* Thanh menu bên trái */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e6ed;
    }
    
    /* ĐỊNH NGHĨA KHỐI CHỮ NHẬT (CARD) */
    .premium-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px; /* Bo góc vừa phải */
        border: 1px solid #e0e6ed; /* Viền mảnh màu xám xanh */
        box-shadow: 0 2px 4px rgba(0,0,0,0.03); /* Đổ bóng cực nhẹ */
        margin-bottom: 25px;
    }
    
    /* Tiêu đề trong khối */
    .card-title {
        color: #b71c1c;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 20px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
    }
    
    /* Nút bấm hình chữ nhật sắc nét */
    .stButton>button {
        background: #b71c1c;
        color: white;
        border-radius: 5px;
        border: none;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: #d32f2f;
        box-shadow: 0 4px 8px rgba(183, 28, 28, 0.2);
    }

    /* Làm gọn các ô nhập liệu */
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LOGIC ĐĂNG NHẬP
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="premium-card" style="text-align:center;">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=60)
        st.markdown('<h2 style="color:#333; font-weight:700;">HỆ THỐNG QUẢN TRỊ</h2>', unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Tài khoản:")
            p = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("XÁC THỰC"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Thông tin không đúng!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. HÀM TẢI DỮ LIỆU
# ==========================================
def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 5. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<br><h3 style='text-align:center;'>DANH MỤC</h3>", unsafe_allow_html=True)
    menu = st.radio("", ["🔎 TRA CỨU TỔNG HỢP", "👤 HỒ SƠ ĐẢNG VIÊN", "📂 KHO VĂN BẢN"])
    st.write("---")
    if st.button("🚪 ĐĂNG XUẤT"):
        st.session_state.admin_auth = False
        st.rerun()

# --- TRANG TRA CỨU ---
if menu == "🔎 TRA CỨU TỔNG HỢP":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔎 CÔNG CỤ TRA CỨU NHANH</div>', unsafe_allow_html=True)
    q = st.text_input("Nhập từ khóa (Tên hoặc nội dung văn bản):")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        df1 = load_data(URL_HOSO)
        df2 = load_data(URL_VANBAN)
        
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👤 KẾT QUẢ HỒ SƠ</div>', unsafe_allow_html=True)
        st.dataframe(df1[df1.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📂 KẾT QUẢ VĂN BẢN</div>', unsafe_allow_html=True)
        st.dataframe(df2[df2.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- TRANG HỒ SƠ ---
elif menu == "👤 HỒ SƠ ĐẢNG VIÊN":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📑 DANH SÁCH ĐẢNG VIÊN</div>', unsafe_allow_html=True)
    st.dataframe(load_data(URL_HOSO), use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">➕ THÊM HỒ SƠ MỚI</div>', unsafe_allow_html=True)
    with st.form("add_hs"):
        c1, c2 = st.columns(2)
        c1.text_input("Họ tên:")
        c2.text_input("Ngày sinh:")
        st.text_input("Chức vụ:")
        st.text_area("Ghi chú:")
        st.form_submit_button("LƯU DỮ LIỆU")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TRANG VĂN BẢN ---
elif menu == "📂 KHO VĂN BẢN":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📤 TẢI LÊN VĂN BẢN</div>', unsafe_allow_html=True)
        st.selectbox("Phân loại:", ["Cấp trên", "Chi bộ", "Báo cáo"])
        st.text_input("Tiêu đề:")
        st.file_uploader("Chọn tệp:", type=['jpg','png','pdf'])
        st.button("XÁC NHẬN LƯU")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 DANH MỤC LƯU TRỮ</div>', unsafe_allow_html=True)
        st.dataframe(load_data(URL_VANBAN), use_container_width=True, height=500)
        st.markdown('</div>', unsafe_allow_html=True)
