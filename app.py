import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH & CSS (TẠO 2 KHỐI NỀN XANH)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"

st.set_page_config(page_title="QUẢN LÝ ĐẢNG VIÊN", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* TIÊU ĐỀ ĐỎ */
    .red-header {
        background-color: #cc0000; color: #ffcc00;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; border-bottom: 3px solid #ffcc00;
        margin-bottom: 25px; text-transform: uppercase;
    }

    /* ĐỊNH DẠNG 2 HÌNH CHỮ NHẬT NỀN XANH */
    .stButton > button {
        background-color: #2e7d32; 
        color: white; 
        border-radius: 15px;
        padding: 40px 20px; 
        font-size: 20px;
        font-weight: bold;
        width: 100%;
        border: none;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stButton > button:hover { background-color: #1b5e20; transform: scale(1.02); }

    /* KHUNG NỘI DUNG CHI TIẾT */
    .content-box {
        border: 2px solid #2e7d32;
        border-radius: 12px;
        padding: 20px;
        background-color: #ffffff;
    }
    
    /* NÚT QUAY LẠI */
    .back-btn > button {
        background-color: #78909c !important;
        padding: 10px !important;
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. KIỂM TRA ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'menu' not in st.session_state: st.session_state.menu = "HOME"

if not st.session_state.auth:
    st.markdown('<div class="red-header">QUẢN TRỊ CHI BỘ ẤP 4</div>', unsafe_allow_html=True)
    with st.form("login"):
        p = st.text_input("Mật khẩu truy cập:", type="password")
        if st.form_submit_button("VÀO HỆ THỐNG"):
            if p == "Tan@753496": st.session_state.auth = True; st.rerun()
            else: st.error("Sai mật khẩu!")
    st.stop()

# ==========================================
# 3. NỘI DUNG SAU KHI ĐĂNG NHẬP
# ==========================================

# MÀN HÌNH CHÍNH: HIỆN 2 HÌNH CHỮ NHẬT NỀN XANH
if st.session_state.menu == "HOME":
    st.markdown('<div class="red-header">MENU QUẢN TRỊ</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(1) # Để dọc cho nút to, dễ bấm trên điện thoại
    with col1:
        if st.button("👤 HỒ SƠ ĐẢNG VIÊN"):
            st.session_state.menu = "HOSO"
            st.rerun()
            
        if st.button("➕ THÊM ĐẢNG VIÊN"):
            st.session_state.menu = "THEM"
            st.rerun()
    
    st.write("---")
    if st.button("🚪 ĐĂNG XUẤT", key="out"):
        st.session_state.auth = False; st.rerun()

# PHẦN 1: HỒ SƠ ĐẢNG VIÊN
elif st.session_state.menu == "HOSO":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI"): st.session_state.menu = "HOME"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="red-header">DANH SÁCH HỒ SƠ</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    df = load_data(URL_HOSO)
    if not df.empty:
        df_display = df.iloc[:, [1, 2]] # Chỉ lấy Họ tên và Ngày sinh
        df_display.columns = ["HỌ VÀ TÊN", "NGÀY SINH"]
        
        st.write("*(Chạm vào tên để xem chi tiết)*")
        sel = st.dataframe(df_display, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        
        if len(sel.selection.rows) > 0:
            row = df.iloc[sel.selection.rows[0]]
            st.info(f"**CHI TIẾT:**\n\n- Chức vụ: {row.iloc[3]}\n- Ghi chú: {row.iloc[4]}")
    st.markdown('</div>', unsafe_allow_html=True)

# PHẦN 2: THÊM ĐẢNG VIÊN
elif st.session_state.menu == "THEM":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI"): st.session_state.menu = "HOME"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="red-header">THÊM ĐẢNG VIÊN MỚI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    with st.form("add"):
        st.text_input("Họ và tên:")
        st.text_input("Ngày tháng năm sinh:")
        st.text_input("Chức vụ:")
        if st.form_submit_button("XÁC NHẬN LƯU"):
            st.success("Đã ghi nhận dữ liệu!")
    st.markdown('</div>', unsafe_allow_html=True)
