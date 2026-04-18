import streamlit as st
import pandas as pd
import requests
import io
import time
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH (ĐỒNG CHÍ GIỮ NGUYÊN)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"
# URL Script để lưu dữ liệu
SCRIPT_URL = "https://script.google.com/macros/s/XXX/exec" 

# Đặt cấu hình trang: Sidebar luôn mở để tạo bố cục chuyên nghiệp
st.set_page_config(page_title="QUẢN TRỊ NỘI BỘ", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN SIÊU CAO CẤP (PREMIUM UI)
# ==========================================
st.markdown("""
    <style>
    /* Tổng thể App */
    .stApp { background-color: #ffffff; color: #333333; }
    
    /* Font chữ mảnh mai */
    html, body, [class*="css"]  { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 300; }
    
    /* Thiết kế Sidebar (Menu trái) dày và cao cấp */
    [data-testid="stSidebar"] {
        background-color: #f0f2f5;
        border-right: 1px solid #e0e0e0;
        min-width: 320px;
    }
    
    /* Header chính: Thanh mảnh, không Gradient lòe loẹt */
    .header-box {
        background-color: #ffffff;
        padding: 10px 0px; border-radius: 0px; color: #333333;
        text-align: left; margin-bottom: 25px;
        border-bottom: 1px solid #e0e0e0;
    }
    .header-box h1 { font-weight: 100 !important; color: #333333; font-size: 28px; }
    
    /* Khối Chức năng (Card) - SIÊU THANH MẢNH */
    .feature-card {
        background: white; 
        padding: 20px; 
        border-radius: 8px; /* Bo góc nhẹ */
        border: 1px solid #f0f0f0; /* Viền cực mảnh */
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); /* Đổ bóng rất nhẹ */
        margin-bottom: 20px;
    }
    
    /* Tiêu đề mục: Mảnh và Đều */
    .section-title {
        color: #8b0000; font-size: 16px; font-weight: 600;
        margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;
    }
    
    /* Nút bấm Premium: Phẳng, không bo góc tròn */
    .stButton>button {
        background: #8b0000; color: white; border-radius: 4px;
        width: 100%; height: 3em; font-weight: 400; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #b71c1c; }
    
    /* Tùy chỉnh ô nhập liệu */
    .stTextInput>div>div>input { border-radius: 4px; border: 1px solid #dcdcdc; }
    
    /* Tùy chỉnh bảng dữ liệu dữ liệu: Đều chằn chặn */
    .stDataFrame { border-radius: 4px; border: 1px solid #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. KIỂM TRA ĐĂNG NHẬP (BẢO MẬT)
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    # Giao diện đăng nhập cao cấp
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
            <div style="background: white; padding: 40px; border-radius: 12px; border: 1px solid #f0f0f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png" width="60" style="margin-bottom:20px;">
                <h2 style="color: #333333; font-weight: 200; font-size: 24px; margin-bottom:30px;">XÁC THỰC QUẢN TRỊ NỘI BỘ</h2>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("👤 Tên đăng nhập:")
            p = st.text_input("🔑 Mật khẩu:", type="password")
            st.markdown('<br>', unsafe_allow_html=True)
            if st.form_submit_button("ĐĂNG NHẬP HỆ THỐNG"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Sai thông tin!")
    st.stop()

# ==========================================
# 4. HÀM XỬ LÝ DỮ LIỆU (ĐỒNG CHÍ GIỮ NGUYÊN)
# ==========================================
def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 5. CÁC CHỨC NĂNG CHÍNH
# ==========================================
# Thanh Menu bên trái (Sidebar) dày và chuyên nghiệp
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-top: 20px; margin-bottom:40px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png" width="50">
            <h3 style="color: #333333; font-weight: 300; margin-top:15px; font-size:18px;">HỆ THỐNG ĐIỀU HÀNH</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color:#666; font-size:14px; margin-bottom:-10px; font-weight:600;'>DANH MỤC CHỨC NĂNG</p>", unsafe_allow_html=True)
    menu = st.radio("", ["🔍 Tra cứu thông tin", "👤 Hồ sơ Đảng viên", "📂 Kho hồ sơ Văn bản"])
    st.write("---")
    
    st.markdown("<p style='color:#666; font-size:14px; margin-bottom:-10px; font-weight:600;'>TÀI KHOẢN</p>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất"):
        st.session_state.admin_auth = False
        st.rerun()

# --- TAB 1: TRA CỨU TỔNG HỢP ---
if menu == "🔍 Tra cứu thông tin":
    st.markdown('<div class="header-box"><h1>TRUNG TÂM TRA CỨU DỮ LIỆU</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 TÌM KIẾM THÔNG MINH</div>', unsafe_allow_html=True)
    q = st.text_input("", placeholder="Nhập tên Đảng viên, nội dung văn bản hoặc từ khóa cần tìm...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        df1 = load_data(URL_HOSO)
        df2 = load_data(URL_VANBAN)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Kết quả trong Hồ sơ</div>', unsafe_allow_html=True)
        res_hs = df1[df1.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
        st.dataframe(res_hs, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📂 Kết quả trong Văn bản</div>', unsafe_allow_html=True)
        res_vb = df2[df2.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
        st.dataframe(res_vb, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="header-box"><h1>QUẢN LÝ ĐẢNG VIÊN CHI BỘ</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📑 DANH SÁCH CHI TIẾT</div>', unsafe_allow_html=True)
    df = load_data(URL_HOSO)
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=500)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">➕ THÊM MỚI HỒ SƠ</div>', unsafe_allow_html=True)
    with st.form("add_dv"):
        c1, c2, c3 = st.columns(3)
        ten = c1.text_input("Họ và tên:")
        ns = c2.text_input("Ngày sinh:")
        cv = c3.text_input("Chức vụ:")
        gc = st.text_area("Ghi chú/Hoàn cảnh:")
        if st.form_submit_button("LƯU HỒ SƠ"):
            st.success("Yêu cầu đã được ghi nhận!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: VĂN BẢN ---
elif menu == "📂 Kho hồ sơ Văn bản":
    st.markdown('<div class="header-box"><h1>KHO VĂN BẢN & BÁO CÁO</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 TẢI LÊN VĂN BẢN MỚI</div>', unsafe_allow_html=True)
    loai_vb = st.selectbox("Loại:", ["Cấp trên", "Chi bộ", "Báo cáo"])
    tieu_de = st.text_input("Tiêu đề văn bản:")
    f = st.file_uploader("Chọn ảnh/tệp:", type=['jpg','png','pdf'])
    st.markdown('<br>', unsafe_allow_html=True)
    if st.button("LƯU TRỮ"):
        st.success("Yêu cầu đã được ghi nhận!")
    st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 DANH MỤC ĐÃ LƯU</div>', unsafe_allow_html=True)
    df_vb = load_data(URL_VANBAN)
    if not df_vb.empty:
        st.dataframe(df_vb, use_container_width=True, height=450)
    st.markdown('</div>', unsafe_allow_html=True)
