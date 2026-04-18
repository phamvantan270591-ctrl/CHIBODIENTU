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
URL_VANBAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"

st.set_page_config(page_title="CHI BỘ ẤP 4 - QUẢN TRỊ", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN TÙY CHỈNH (CSS CAO CẤP)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }

    /* --- PHẦN ĐĂNG NHẬP --- */
    .login-container { max-width: 400px; margin: 0 auto; }
    .login-header-mini {
        background-color: #cc0000; padding: 15px;
        border-radius: 10px 10px 0px 0px; text-align: center;
        border-bottom: 2px solid #ffcc00;
    }
    .login-header-mini h2 {
        color: #ffcc00; font-weight: 700; font-size: 1.1rem;
        margin: 0; text-transform: uppercase;
    }
    .login-box-mini {
        background: white; padding: 25px;
        border-radius: 0px 0px 10px 10px; border: 1px solid #e0e6ed;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* --- PHẦN HỒ SƠ ĐẢNG VIÊN (XANH LÁ) --- */
    .green-container {
        border: 2px solid #2e7d32; border-radius: 10px;
        padding: 20px; background-color: #ffffff; margin-bottom: 25px;
    }
    .green-title {
        color: #1b5e20; font-weight: bold; font-size: 1.2rem;
        text-transform: uppercase; border-bottom: 2px solid #2e7d32;
        padding-bottom: 8px; margin-bottom: 15px;
    }
    .green-sub-card {
        background-color: #f1f8e9; border: 1px solid #c8e6c9;
        border-radius: 8px; padding: 15px; margin-top: 10px;
    }

    /* --- CHUNG --- */
    .stButton>button {
        background: #cc0000; color: white; border-radius: 6px;
        font-weight: bold; width: 100%; height: 3em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Hàm tải dữ liệu
def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 3. LOGIC ĐĂNG NHẬP
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown('<div style="height: 15vh;"></div>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header-mini"><h2>Hệ thống quản trị chi bộ Ấp 4</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="login-box-mini">', unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Tài khoản:", value="Admin")
            p = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("XÁC NHẬN TRUY CẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Sai thông tin đăng nhập!")
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. GIAO DIỆN CHÍNH SAU ĐĂNG NHẬP
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding:10px; background:#cc0000; border-radius:8px; margin-bottom:20px;">
            <p style="color:#ffcc00; font-weight:bold; margin:0; font-size: 1.1rem;">CHI BỘ ẤP 4</p>
        </div>
    """, unsafe_allow_html=True)
    menu = st.radio("LỰA CHỌN CHỨC NĂNG:", ["🔍 Tra cứu nhanh", "👤 Hồ sơ Đảng viên", "📂 Kho Văn bản"])
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.admin_auth = False
        st.rerun()

# --- MỤC 1: TRA CỨU ---
if menu == "🔍 Tra cứu nhanh":
    st.markdown("### 🔎 TRA CỨU TỔNG HỢP")
    st.info("Nhập từ khóa để tìm kiếm trong toàn bộ hệ thống.")
    q = st.text_input("Từ khóa tìm kiếm (Tên, nội dung...):")

# --- MỤC 2: HỒ SƠ ĐẢNG VIÊN (THEO YÊU CẦU MÀU XANH LÁ) ---
elif menu == "👤 Hồ sơ Đảng viên":
    # Khối bao quanh màu xanh lá
    st.markdown('<div class="green-container">', unsafe_allow_html=True)
    st.markdown('<div class="green-title">📂 QUẢN LÝ HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)

    # Chia 2 phần trong khối xanh
    tab_ds, tab_them = st.tabs(["📋 DANH SÁCH ĐẢNG VIÊN", "➕ THÊM ĐẢNG VIÊN MỚI"])

    with tab_ds:
        st.markdown('<div class="green-sub-card">', unsafe_allow_html=True)
        df_hs = load_data(URL_HOSO)
        if not df_hs.empty:
            # Chỉ hiển thị STT và Họ Tên
            df_view = df_hs.iloc[:, [0, 1]]
            df_view.columns = ["STT", "HỌ VÀ TÊN"]
            
            st.write("*(Chạm vào dòng để xem chi tiết bên dưới)*")
            selected = st.dataframe(
                df_view, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="single-row"
            )

            # Hiện chi tiết khi bấm vào dòng
            if len(selected.selection.rows) > 0:
                idx = selected.selection.rows[0]
                row = df_hs.iloc[idx]
                st.markdown("---")
                st.subheader(f"🔍 Chi tiết: {row.iloc[1]}")
                c1, c2 = st.columns(2)
                c1.write(f"**Số thứ tự:** {row.iloc[0]}")
                c1.write(f"**Ngày sinh:** {row.iloc[2]}")
                c2.write(f"**Chức vụ:** {row.iloc[3]}")
                c2.write(f"**Ghi chú:** {row.iloc[4]}")
        else:
            st.warning("Chưa có dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_them:
        st.markdown('<div class="green-sub-card">', unsafe_allow_html=True)
        with st.form("add_new"):
            st.write("**NHẬP THÔNG TIN ĐẢNG VIÊN**")
            stt = st.text_input("Số thứ tự:")
            ten = st.text_input("Họ và tên:")
            ns = st.text_input("Ngày sinh:")
            cv = st.text_input("Chức vụ:")
            gc = st.text_area("Ghi chú:")
            if st.form_submit_button("LƯU DỮ LIỆU"):
                st.success(f"Đã nhận hồ sơ của đồng chí {ten}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MỤC 3: VĂN BẢN ---
elif menu == "📂 Kho Văn bản":
    st.markdown("### 📂 LƯU TRỮ VĂN BẢN")
    st.file_uploader("Chọn ảnh văn bản:", type=['jpg','png','pdf'])
    st.button("XÁC NHẬN LƯU")
