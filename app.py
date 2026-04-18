import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH & CSS (PHONG CÁCH KHỐI ĐỒNG NHẤT)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"

st.set_page_config(page_title="CHI BỘ ẤP 4", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* KHỐI TIÊU ĐỀ ĐỎ GỌN NHỎ */
    .red-header {
        background-color: #cc0000; color: #ffcc00;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; border-bottom: 2px solid #ffcc00;
        margin-bottom: 20px; text-transform: uppercase;
    }

    /* KHỐI CHỮ NHẬT LỚN MÀU XANH LÁ (HỒ SƠ ĐẢNG VIÊN) */
    .outer-green-box {
        background-color: #ffffff;
        border: 2px solid #2e7d32;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
    }

    /* KHỐI CHỮ NHẬT CON MÀU XANH LÁ (BÊN TRONG) */
    .inner-green-box {
        background-color: #f1f8e9;
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .green-label {
        color: #1b5e20; font-weight: bold; font-size: 1.1rem;
        margin-bottom: 5px; display: block;
    }

    /* NÚT BẤM TO (GIỐNG HÌNH CHỤP) */
    .stButton > button {
        background-color: #2e7d32; color: white; border-radius: 12px;
        padding: 20px; font-weight: bold; width: 100%; border: none;
        margin-bottom: 10px;
    }
    .stButton > button:hover { background-color: #1b5e20; }
    
    /* NÚT QUAY LẠI MÀU XÁM */
    .back-btn > button { background-color: #78909c !important; padding: 10px !important; }

    /* KHUNG CHI TIẾT TRẮNG */
    .detail-white-card {
        background: white; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #2e7d32; margin-top: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. XỬ LÝ ĐĂNG NHẬP
# ==========================================
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
if 'page_state' not in st.session_state: st.session_state.page_state = "MENU"

if not st.session_state.admin_auth:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="red-header">Hệ thống quản trị chi bộ Ấp 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="outer-green-box">', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Tài khoản:", value="Admin")
        p = st.text_input("Mật khẩu:", type="password")
        if st.form_submit_button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496": 
                st.session_state.admin_auth = True; st.rerun()
            else: st.error("Sai mật khẩu!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. NỘI DUNG CHÍNH (FULL KHỐI)
# ==========================================

# --- MÀN HÌNH CHÍNH ---
if st.session_state.page_state == "MENU":
    st.markdown('<div class="red-header">MENU QUẢN TRỊ</div>', unsafe_allow_html=True)
    
    if st.button("👤 HỒ SƠ ĐẢNG VIÊN"):
        st.session_state.page_state = "HOSO"
        st.rerun()
        
    if st.button("📤 THÊM VĂN BẢN MỚI"):
        st.session_state.page_state = "VANBAN"
        st.rerun()

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    if st.button("🚪 THOÁT HỆ THỐNG"):
        st.session_state.admin_auth = False
        st.rerun()

# --- MÀN HÌNH 1: HỒ SƠ ĐẢNG VIÊN (KHỐI TRONG KHỐI) ---
elif st.session_state.page_state == "HOSO":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI MENU"):
        st.session_state.page_state = "MENU"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # KHỐI LỚN XANH LÁ
    st.markdown('<div class="outer-green-box">', unsafe_allow_html=True)
    st.markdown('<span class="green-label">📂 HỒ SƠ ĐẢNG VIÊN</span>', unsafe_allow_html=True)

    # Khối con 1: Danh sách
    st.markdown('<div class="inner-green-box">', unsafe_allow_html=True)
    st.markdown('<span class="green-label">📋 DANH SÁCH ĐẢNG VIÊN</span>', unsafe_allow_html=True)
    
    df = load_data(URL_HOSO)
    if not df.empty:
        df_view = df.iloc[:, [0, 1]]
        df_view.columns = ["STT", "HỌ VÀ TÊN"]
        
        # Bảng chọn dòng
        selected = st.dataframe(df_view, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

        # Khối chi tiết màu trắng nằm trong khối xanh con
        if len(selected.selection.rows) > 0:
            row = df.iloc[selected.selection.rows[0]]
            st.markdown(f"""
                <div class="detail-white-card">
                    <p style="color:#1b5e20; font-weight:bold; border-bottom:1px solid #eee;">THÔNG TIN CHI TIẾT</p>
                    <p><b>Họ và tên:</b> {row.iloc[1]}</p>
                    <p><b>Ngày sinh:</b> {row.iloc[2]}</p>
                    <p><b>Chức vụ:</b> {row.iloc[3]}</p>
                    <p><b>Ghi chú:</b> {row.iloc[4]}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Đang tải dữ liệu...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Khối con 2: Thêm mới
    st.markdown('<div class="inner-green-box">', unsafe_allow_html=True)
    st.markdown('<span class="green-label">➕ THÊM ĐẢNG VIÊN</span>', unsafe_allow_html=True)
    with st.form("form_add", clear_on_submit=True):
        ten = st.text_input("Nhập họ tên:")
        ngay = st.text_input("Nhập ngày sinh:")
        if st.form_submit_button("XÁC NHẬN LƯU"):
            st.success(f"Đã ghi nhận: {ten}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Kết thúc khối lớn

# --- MÀN HÌNH 2: VĂN BẢN ---
elif st.session_state.page_state == "VANBAN":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI MENU"):
        st.session_state.page_state = "MENU"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="outer-green-box">', unsafe_allow_html=True)
    st.markdown('<span class="green-label">📤 QUẢN LÝ VĂN BẢN</span>', unsafe_allow_html=True)
    st.file_uploader("Chọn ảnh văn bản từ điện thoại:", type=['jpg','png','pdf'])
    st.button("TẢI LÊN NGAY")
    st.markdown('</div>', unsafe_allow_html=True)
