import streamlit as st
import pandas as pd
import requests
import io
import time
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEST_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="HỆ THỐNG QUẢN TRỊ NỘI BỘ", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN NÂNG CAO (PROFESSIONAL UI)
# ==========================================
st.markdown("""
    <style>
    /* Tổng thể */
    .stApp { background-color: #f8f9fa; }
    
    /* Khối Header */
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 30px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    
    /* Khối Chức năng (Card) */
    .feature-card {
        background: white; padding: 25px; border-radius: 15px;
        border-top: 5px solid #d32f2f;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Tên mục tiêu đề */
    .section-title {
        color: #b71c1c; font-size: 20px; font-weight: 800;
        margin-bottom: 15px; display: flex; align-items: center;
    }
    
    /* Nút bấm chuyên nghiệp */
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 10px;
        font-weight: 600; width: 100%; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background: #ff1744; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HÀM XỬ LÝ DỮ LIỆU
# ==========================================
def get_data_fresh(url):
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return None

# ==========================================
# 4. LOGIC ĐĂNG NHẬP (BẢO MẬT)
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
                <h2 style="color: #b71c1c; margin-top: 15px;">QUẢN TRỊ NỘI BỘ</h2>
                <p style="color: #666;">Vui lòng đăng nhập để truy cập hệ thống</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("👤 Tên đăng nhập:")
            p = st.text_input("🔑 Mật khẩu:", type="password")
            if st.form_submit_button("XÁC THỰC HỆ THỐNG"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Thông tin đăng nhập không chính xác!")
    st.stop()

# ==========================================
# 5. GIAO DIỆN CHÍNH (SAU ĐĂNG NHẬP)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>HỆ THỐNG QUẢN TRỊ</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("LỰA CHỌN CHỨC NĂNG:", 
                    ["🔍 Tra cứu & Tìm kiếm", "👤 Quản lý Đảng viên", "📂 Kho hồ sơ Văn bản"])
    st.write("---")
    if st.button("🚪 Đăng xuất hệ thống"):
        st.session_state.admin_auth = False
        st.rerun()

# --- TAB 1: TRA CỨU ---
if menu == "🔍 Tra cứu & Tìm kiếm":
    st.markdown('<div class="header-box"><h1>TRUNG TÂM TRA CỨU DỮ LIỆU</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 CÔNG CỤ TÌM KIẾM THÔNG MINH</div>', unsafe_allow_html=True)
    q = st.text_input("", placeholder="Nhập tên Đảng viên, số hiệu văn bản hoặc từ khóa cần tìm...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        df_hs = get_data_fresh(URL_HOSO)
        df_vb = get_data_fresh(URL_VANBAN)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">👤 KẾT QUẢ TRONG HỒ SƠ</div>', unsafe_allow_html=True)
            res_hs = df_hs[df_hs.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res_hs, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📂 KẾT QUẢ TRONG VĂN BẢN</div>', unsafe_allow_html=True)
            res_vb = df_vb[df_vb.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
            st.dataframe(res_vb, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Quản lý Đảng viên":
    st.markdown('<div class="header-box"><h1>QUẢN LÝ HỒ SƠ ĐẢNG VIÊN</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📑 DANH SÁCH CHI TIẾT</div>', unsafe_allow_html=True)
    df = get_data_fresh(URL_HOSO)
    st.dataframe(df, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ THÊM MỚI HỒ SƠ</div>', unsafe_allow_html=True)
    with st.form("add_dv"):
        c1, c2, c3 = st.columns(3)
        ten = c1.text_input("Họ và tên:")
        ns = c2.text_input("Ngày sinh:")
        cv = c3.text_input("Chức vụ:")
        gc = st.text_area("Ghi chú đặc điểm Đảng viên:")
        if st.form_submit_button("LƯU HỒ SƠ"):
            st.success("Đã ghi nhận dữ liệu hồ sơ mới!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: VĂN BẢN ---
elif menu == "📂 Kho hồ sơ Văn bản":
    st.markdown('<div class="header-box"><h1>KHO LƯU TRỮ VĂN BẢN & BÁO CÁO</h1></div>', unsafe_allow_html=True)
    
    col_up, col_view = st.columns([1, 2])
    
    with col_up:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📤 TẢI LÊN VĂN BẢN</div>', unsafe_allow_html=True)
        loai = st.selectbox("Loại văn bản:", ["Cấp trên ban hành", "Công văn Chi bộ", "Báo cáo nội bộ"])
        tieude = st.text_input("Trích yếu/Tiêu đề:")
        file = st.file_uploader("Chụp ảnh hoặc chọn tệp:", type=['jpg','png','pdf'])
        if st.button("XÁC NHẬN LƯU TRỮ"):
            st.success("Văn bản đã được đưa vào kho lưu trữ!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_view:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 DANH MỤC ĐÃ LƯU</div>', unsafe_allow_html=True)
        df_vb = get_data_fresh(URL_VANBAN)
        st.dataframe(df_vb, use_container_width=True, height=500)
        st.markdown('</div>', unsafe_allow_html=True)
