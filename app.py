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
    .red-header {
        background-color: #cc0000; color: #ffcc00;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; border-bottom: 3px solid #ffcc00;
        margin-bottom: 25px; text-transform: uppercase;
    }
    /* 2 KHỐI HÌNH CHỮ NHẬT NỀN XANH */
    .stButton > button {
        background-color: #2e7d32; color: white; border-radius: 15px;
        padding: 40px 20px; font-size: 20px; font-weight: bold;
        width: 100%; border: none; margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .content-box {
        border: 2px solid #2e7d32; border-radius: 12px;
        padding: 20px; background-color: #ffffff;
    }
    .back-btn > button {
        background-color: #78909c !important; padding: 10px !important; font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# HÀM TẢI DỮ LIỆU CÓ KIỂM TRA LỖI
def load_data(url):
    try:
        # Thêm nocache để dữ liệu luôn mới
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        r.raise_for_status() 
        df = pd.read_csv(io.StringIO(r.text))
        return df.fillna("Chưa có")
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        return pd.DataFrame()

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
            if p == "Tan@753496": 
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("Sai mật khẩu!")
    st.stop()

# ==========================================
# 3. NỘI DUNG SAU KHI ĐĂNG NHẬP
# ==========================================

# MÀN HÌNH CHÍNH: 2 HÌNH CHỮ NHẬT XANH
if st.session_state.menu == "HOME":
    st.markdown('<div class="red-header">MENU QUẢN TRỊ</div>', unsafe_allow_html=True)
    
    # Nút 1
    if st.button("👤 HỒ SƠ ĐẢNG VIÊN"):
        st.session_state.menu = "HOSO"
        st.rerun()
        
    # Nút 2
    if st.button("➕ THÊM ĐẢNG VIÊN"):
        st.session_state.menu = "THEM"
        st.rerun()
    
    st.write("---")
    if st.button("🚪 ĐĂNG XUẤT"):
        st.session_state.auth = False
        st.rerun()

# PHẦN 1: HỒ SƠ ĐẢNG VIÊN
elif st.session_state.menu == "HOSO":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI"): 
        st.session_state.menu = "HOME"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="red-header">DANH SÁCH HỒ SƠ</div>', unsafe_allow_html=True)
    
    df = load_data(URL_HOSO)
    
    if not df.empty:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        # Kiểm tra nếu file có ít nhất 2 cột (Họ tên, Ngày sinh)
        if df.shape[1] >= 2:
            df_display = df.iloc[:, [1, 2]] 
            df_display.columns = ["HỌ VÀ TÊN", "NGÀY SINH"]
            
            st.write("*(Chạm vào tên để xem chi tiết)*")
            sel = st.dataframe(df_display, use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
            
            if len(sel.selection.rows) > 0:
                idx = sel.selection.rows[0]
                row = df.iloc[idx]
                # Hiện chi tiết
                st.info(f"**THÔNG TIN CHI TIẾT:**\n\n- Họ tên: {row.iloc[1]}\n- Ngày sinh: {row.iloc[2]}\n- Chức vụ: {row.iloc[3] if df.shape[1]>3 else 'N/A'}\n- Ghi chú: {row.iloc[4] if df.shape[1]>4 else 'N/A'}")
        else:
            st.warning("File dữ liệu không đúng cấu trúc cột.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Không thể tải dữ liệu từ Sheets. Hãy kiểm tra lại kết nối mạng.")

# PHẦN 2: THÊM ĐẢNG VIÊN
elif st.session_state.menu == "THEM":
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ QUAY LẠI"): 
        st.session_state.menu = "HOME"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="red-header">THÊM ĐẢNG VIÊN MỚI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Họ và tên:")
        dob = st.text_input("Ngày tháng năm sinh:")
        pos = st.text_input("Chức vụ:")
        if st.form_submit_button("XÁC NHẬN LƯU"):
            if name:
                st.success(f"Đã ghi nhận tạm thời: {name}")
            else:
                st.error("Vui lòng nhập họ tên!")
    st.markdown('</div>', unsafe_allow_html=True)
