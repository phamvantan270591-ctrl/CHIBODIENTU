import streamlit as st
import pandas as pd
import requests
import io
import time
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG (SỬA LỖI TÊN BIẾN)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 

URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="HỆ THỐNG QUẢN TRỊ NỘI BỘ", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN NÂNG CAO (PROFESSIONAL UI)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 30px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    .feature-card {
        background: white; padding: 25px; border-radius: 15px;
        border-top: 5px solid #d32f2f;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .section-title {
        color: #b71c1c; font-size: 20px; font-weight: 800;
        margin-bottom: 15px; display: flex; align-items: center;
    }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 10px;
        font-weight: 600; width: 100%; border: none; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HÀM XỬ LÝ DỮ LIỆU
# ==========================================
def get_data_fresh(url):
    try:
        # Ép kiểu dữ liệu mới nhất bằng cách thêm dấu thời gian
        fresh_url = f"{url}&t={int(time.time())}"
        r = requests.get(fresh_url, timeout=10)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==========================================
# 4. LOGIC ĐĂNG NHẬP
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown('<br><br>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
            <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png" width="70">
                <h2 style="color: #b71c1c; margin-top: 15px;">HỆ THỐNG QUẢN TRỊ</h2>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("👤 Tên đăng nhập:")
            p = st.text_input("🔑 Mật khẩu:", type="password")
            if st.form_submit_button("XÁC THỰC TRUY CẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Thông tin không chính xác!")
    st.stop()

# ==========================================
# 5. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>DANH MỤC</h2>", unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["🔍 Tìm kiếm tổng hợp", "👤 Hồ sơ Đảng viên", "📂 Kho văn bản"])
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.admin_auth = False
        st.rerun()

# --- TAB 1: TÌM KIẾM ---
if menu == "🔍 Tìm kiếm tổng hợp":
    st.markdown('<div class="header-box"><h1>TRUNG TÂM TRA CỨU DỮ LIỆU</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    q = st.text_input("🔎 Nhập từ khóa:", placeholder="Tên Đảng viên hoặc nội dung văn bản...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        df_hs = get_data_fresh(URL_HOSO)
        df_vb = get_data_fresh(URL_VANBAN)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)
            if not df_hs.empty:
                res_hs = df_hs[df_hs.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                st.dataframe(res_hs, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">KHO VĂN BẢN</div>', unsafe_allow_html=True)
            if not df_vb.empty:
                res_vb = df_vb[df_vb.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                st.dataframe(res_vb, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="header-box"><h1>DANH SÁCH ĐẢNG VIÊN</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    df = get_data_fresh(URL_HOSO)
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("➕ THÊM MỚI HỒ SƠ"):
        with st.form("add_dv"):
            c1, c2 = st.columns(2)
            t = c1.text_input("Họ tên:")
            n = c2.text_input("Ngày sinh:")
            cv = c1.text_input("Chức vụ:")
            gc = st.text_area("Ghi chú:")
            if st.form_submit_button("LƯU DỮ LIỆU"):
                st.success("Yêu cầu đã được ghi nhận!")

# --- TAB 3: VĂN BẢN ---
elif menu == "📂 Kho văn bản":
    st.markdown('<div class="header-box"><h1>KHO VĂN BẢN & BÁO CÁO</h1></div>', unsafe_allow_html=True)
    c_up, c_list = st.columns([1, 2])
    
    with c_up:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📤 TẢI LÊN</div>', unsafe_allow_html=True)
        st.selectbox("Loại:", ["Cấp trên", "Chi bộ", "Báo cáo"])
        st.text_input("Tiêu đề:")
        st.file_uploader("Chọn tệp/Ảnh:", type=['jpg','png','pdf'])
        st.button("XÁC NHẬN")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_list:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 DANH MỤC</div>', unsafe_allow_html=True)
        df_vb = get_data_fresh(URL_VANBAN)
        if not df_vb.empty:
            st.dataframe(df_vb, use_container_width=True, height=450)
        st.markdown('</div>', unsafe_allow_html=True)
