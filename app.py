import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import io
import time

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link xuất bản thô để đảm bảo định dạng chuẩn
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
CONFIG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CauHinh"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ẤP 4", layout="centered")

# --- CSS GIỮ NGUYÊN GIAO DIỆN CHUYÊN NGHIỆP ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .header-container {
        background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
        padding: 40px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin: -65px -20px 30px -20px;
    }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .info-box { background: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 5px solid #d32f2f; margin-bottom: 10px; font-size: 15px; }
    .stButton>button { background: #d32f2f; color: white; border-radius: 12px; font-weight: 700; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

def get_data_utf8(url):
    """Hàm tải dữ liệu và ÉP KIỂU mã hóa UTF-8 để sửa lỗi tiếng Việt"""
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        r.encoding = 'utf-8' # Ép mã hóa UTF-8 từ phản hồi của server
        if r.status_code == 200:
            # Đọc dữ liệu với encoding utf-8
            return pd.read_csv(io.StringIO(r.text), dtype=str, encoding='utf-8').fillna("")
        return None
    except Exception as e:
        return None

# --- LOGIC XÁC THỰC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header-container"><h1>🇻🇳 CHI BỘ ẤP 4</h1><p>Hệ thống thông tin Đảng viên</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt = st.text_input("📱 Nhập số điện thoại:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                df_dv = get_data_utf8(CSV_URL)
                if df_dv is not None:
                    target = clean_num(sdt)
                    match = None
                    for _, row in df_dv.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt, "data": match}
                        st.rerun()
                    else: st.error("❌ Không tìm thấy SĐT trong danh sách.")
                else: st.error("⚠️ Lỗi kết nối hoặc quyền chia sẻ Sheets.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    # Lấy tên Đ/c từ data đã sửa lỗi phông
    ten_dc = "Đồng chí"
    for v in u['data'].values():
        if v and not str(v).isdigit() and len(str(v)) > 2:
            ten_dc = str(v); break

    st.markdown(f'<div class="header-container"><h2>Chào Đ/c {ten_dc}</h2></div>', unsafe_allow_html=True)

    with st.sidebar:
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ", "👤 Hồ sơ cá nhân"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if menu == "👤 Hồ sơ cá nhân":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#d32f2f;">THÔNG TIN ĐẢNG VIÊN</h3>', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                # Hiển thị thông tin đã được xử lý UTF-8
                st.markdown(f'<div class="info-box"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ... (Các phần khác giữ nguyên logic như bản trước) ...
    elif menu == "🏠 Trang chủ":
        st.info("Phần này hiển thị thông báo họp và điểm danh (Đã tích hợp xử lý UTF-8)")
        # Code phần Trang chủ của đồng chí dán vào đây
