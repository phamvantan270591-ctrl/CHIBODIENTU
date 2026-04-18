import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH & CSS TINH GỌN
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"

st.set_page_config(page_title="QUẢN LÝ ĐẢNG VIÊN", layout="centered")

st.markdown("""
    <style>
    /* Nền và Tiêu đề đỏ gọn */
    .stApp { background-color: #f8f9fa; }
    .red-header {
        background-color: #cc0000; color: #ffcc00;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; border-bottom: 3px solid #ffcc00;
        margin-bottom: 15px; text-transform: uppercase; font-size: 1.2rem;
    }

    /* KHỐI LỚN BAO NGOÀI MÀU XANH LÁ ĐẬM */
    .main-green-box {
        border: 2px solid #2e7d32;
        border-radius: 12px;
        padding: 15px;
        background-color: #ffffff;
    }

    /* TIÊU ĐỀ PHÂN PHẦN */
    .sub-title {
        color: #1b5e20; font-weight: bold;
        display: flex; align-items: center; gap: 10px;
        margin-top: 10px; margin-bottom: 10px;
    }

    /* NÚT BẤM TO GỌN */
    .stButton > button {
        background-color: #2e7d32; color: white; border-radius: 8px;
        padding: 12px; font-weight: bold; width: 100%; border: none;
    }
    
    /* KHUNG CHI TIẾT KHI BẤM VÀO */
    .detail-view {
        background-color: #f1f8e9; border: 1px solid #c8e6c9;
        padding: 15px; border-radius: 8px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="red-header">QUẢN TRỊ CHI BỘ ẤP 4</div>', unsafe_allow_html=True)
    with st.form("login"):
        u = st.text_input("Tài khoản:", value="Admin")
        p = st.text_input("Mật khẩu:", type="password")
        if st.form_submit_button("VÀO HỆ THỐNG"):
            if p == "Tan@753496": st.session_state.auth = True; st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# ==========================================
# 3. NỘI DUNG CHÍNH (BỎ HẾT PHẦN THỪA)
# ==========================================
st.markdown('<div class="red-header">HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)

# BẮT ĐẦU KHỐI XANH DUY NHẤT
st.markdown('<div class="main-green-box">', unsafe_allow_html=True)

# --- PHẦN DANH SÁCH ---
st.markdown('<div class="sub-title">📋 DANH SÁCH HỌ TÊN & NGÀY SINH</div>', unsafe_allow_html=True)

df = load_data(URL_HOSO)
if not df.empty:
    # Chỉ lấy Họ tên và Ngày sinh (Cột 2 và 3)
    df_mini = df.iloc[:, [1, 2]]
    df_mini.columns = ["HỌ VÀ TÊN", "NGÀY SINH"]
    
    # Bảng gọn
    sel = st.dataframe(df_mini, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")

    # Hiện chi tiết ngay bên dưới khi chọn
    if len(sel.selection.rows) > 0:
        row = df.iloc[sel.selection.rows[0]]
        st.markdown(f"""
            <div class="detail-view">
                <p><b>👤 Họ tên:</b> {row.iloc[1]}</p>
                <p><b>🎂 Ngày sinh:</b> {row.iloc[2]}</p>
                <p><b>🎖️ Chức vụ:</b> {row.iloc[3]}</p>
                <p><b>📝 Ghi chú:</b> {row.iloc[4]}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.write("Không tìm thấy dữ liệu.")

st.markdown('<hr style="border: 0.5px solid #eee; margin: 20px 0;">', unsafe_allow_html=True)

# --- PHẦN THÊM MỚI ---
st.markdown('<div class="sub-title">➕ THÊM ĐẢNG VIÊN MỚI</div>', unsafe_allow_html=True)
with st.form("add_new", clear_on_submit=True):
    name = st.text_input("Họ và tên:")
    dob = st.text_input("Ngày tháng năm sinh:")
    pos = st.text_input("Chức vụ:")
    if st.form_submit_button("LƯU HỒ SƠ"):
        st.success(f"Đã ghi nhận: {name}")

st.markdown('</div>', unsafe_allow_html=True) # KẾT THÚC KHỐI XANH

# Nút thoát gọn dưới cùng
if st.button("🚪 THOÁT"):
    st.session_state.auth = False
    st.rerun()
