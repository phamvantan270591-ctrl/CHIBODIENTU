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
# 2. GIAO DIỆN TÙY CHỈNH (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Nền tổng thể */
    .stApp { background-color: #fdfdfd; }

    /* Khung tiêu đề Đăng nhập màu đỏ cờ */
    .login-header {
        background-color: #cc0000;
        padding: 20px;
        border-radius: 8px 8px 0px 0px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 3px solid #ffcc00; /* Đường viền vàng dưới chân */
    }
    
    .login-header h2 {
        color: #ffcc00; /* Chữ vàng */
        font-weight: 800;
        margin-left: 15px;
        font-size: 1.5rem;
        text-transform: uppercase;
    }

    /* Khối chứa Form đăng nhập */
    .login-box {
        background: white;
        padding: 30px;
        border-radius: 0px 0px 8px 8px;
        border: 1px solid #eeeeee;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }

    /* Khối chức năng bên trong App */
    .premium-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    /* Chỉnh nút bấm */
    .stButton>button {
        background: #cc0000;
        color: white;
        border-radius: 4px;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. PHẦN ĐĂNG NHẬP (CẬP NHẬT HÌNH CỜ ĐẢNG KHÔNG LỖI)
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown('<br><br><br>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.3, 1])
    
    with col_m:
        # Sử dụng mã SVG để vẽ hình Búa Liềm (Đảm bảo không bao giờ lỗi hình)
        st.markdown("""
            <div class="login-header">
                <svg width="50" height="50" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 50L80 50M50 20L50 80" stroke="#ffcc00" stroke-width="8" stroke-linecap="round"/>
                    <path d="M30 30C40 20 60 20 70 30C80 40 80 60 70 70C60 80 40 80 30 70C20 60 20 40 30 30Z" stroke="#ffcc00" stroke-width="5"/>
                    <circle cx="50" cy="50" r="10" fill="#ffcc00"/>
                </svg>
                <div style="margin-left: 15px; text-align: left;">
                    <h2 style="margin: 0; line-height: 1.2;">Hệ thống quản trị</h2>
                    <h2 style="margin: 0; line-height: 1.2; font-size: 1.3rem; color: #ffffff;">Chi bộ Ấp 4</h2>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Khối nhập liệu bên dưới
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        with st.form("login_form"):
            # Chỉnh lại nhãn cho chuyên nghiệp
            u = st.text_input("👤 Tài khoản:", value="Admin")
            p = st.text_input("🔑 Mật khẩu:", type="password")
            st.markdown('<br>', unsafe_allow_html=True)
            if st.form_submit_button("XÁC NHẬN TRUY CẬP"):
                # Mật khẩu đồng chí yêu cầu: Tan@753496
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.success("Đăng nhập thành công!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Thông tin đăng nhập không chính xác!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. GIAO DIỆN SAU KHI VÀO HỆ THỐNG
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#cc0000; border-radius:5px; margin-bottom:20px;">
            <p style="color:#ffcc00; font-weight:bold; margin:0;">CHI BỘ ẤP 4</p>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["🔍 Tìm kiếm", "👤 Đảng viên", "📂 Văn bản"])
    if st.button("🚪 Thoát"):
        st.session_state.admin_auth = False
        st.rerun()

# Dữ liệu mẫu (Đồng chí thay bằng hàm load_data của mình)
if menu == "🔍 Tìm kiếm":
    st.markdown("### 🔎 TRA CỨU DỮ LIỆU")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.text_input("Nhập từ khóa tìm kiếm...")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "👤 Đảng viên":
    st.markdown("### 👤 DANH SÁCH ĐẢNG VIÊN")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.write("Dữ liệu Đảng viên sẽ hiển thị tại đây.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📂 Văn bản":
    st.markdown("### 📂 KHO VĂN BẢN & BÁO CÁO")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.file_uploader("Tải lên văn bản mới...")
    st.markdown('</div>', unsafe_allow_html=True)
