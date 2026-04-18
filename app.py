import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH CƠ BẢN
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="CHI BỘ ẤP 4 - QUẢN TRỊ", layout="wide")

# ==========================================
# 2. GIAO DIỆN TÙY CHỈNH (CSS CAO CẤP)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }

    /* Container bao quanh để căn giữa */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
    }

    /* Khung tiêu đề đỏ: Gọn nhỏ, chữ vàng, căn giữa */
    .login-header-mini {
        background-color: #cc0000;
        padding: 15px;
        border-radius: 10px 10px 0px 0px;
        text-align: center;
        border-bottom: 2px solid #ffcc00;
    }
    
    .login-header-mini h2 {
        color: #ffcc00;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Khối chứa Form: Bo sát khối đỏ, thanh mảnh */
    .login-box-mini {
        background: white;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .premium-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e6ed;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background: #cc0000;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
        height: 3em;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. PHẦN ĐĂNG NHẬP (GỌN NHỎ & CÂN ĐỐI)
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    # Đẩy khối đăng nhập xuống giữa màn hình một chút
    st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
    
    # Sử dụng cột để căn giữa tuyệt đối
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    
    with col_m:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Tiêu đề đỏ gọn nhỏ
        st.markdown("""
            <div class="login-header-mini">
                <h2>Hệ thống quản trị chi bộ Ấp 4</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Form đăng nhập thanh mảnh
        st.markdown('<div class="login-box-mini">', unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Tài khoản:", value="Admin")
            p = st.text_input("Mật khẩu:", type="password")
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            if st.form_submit_button("XÁC NHẬN TRUY CẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.success("Đang vào hệ thống...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Sai thông tin đăng nhập!")
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#cc0000; border-radius:8px; margin-bottom:20px;">
            <p style="color:#ffcc00; font-weight:bold; margin:0; font-size: 1.1rem;">CHI BỘ ẤP 4</p>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("MENU ĐIỀU HÀNH:", ["🔍 Tra cứu nhanh", "👤 Hồ sơ Đảng viên", "📂 Kho Văn bản"])
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.admin_auth = False
        st.rerun()

# --- NỘI DUNG CHI TIẾT ---
if menu == "🔍 Tra cứu nhanh":
    st.markdown("### 🔎 HỆ THỐNG TRA CỨU")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    q = st.text_input("Nhập tên Đảng viên hoặc từ khóa cần tìm:")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "👤 Hồ sơ Đảng viên":
    st.markdown("### 👤 QUẢN LÝ HỒ SƠ")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.info("Danh sách Đảng viên chi bộ Ấp 4.")
    # Chỗ này đồng chí có thể dùng st.dataframe(df) để hiện bảng
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📂 Kho Văn bản":
    st.markdown("### 📂 KHO LƯU TRỮ VĂN BẢN")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.file_uploader("Chọn ảnh văn bản/báo cáo từ thiết bị:", type=['jpg','png','pdf'])
    st.button("LƯU VÀO KHO")
    st.markdown('</div>', unsafe_allow_html=True)
