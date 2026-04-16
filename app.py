import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link lấy dữ liệu (ép kiểu lấy toàn bộ bảng)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .profile-card { padding: 20px; border-radius: 15px; border-left: 10px solid #d32f2f; background-color: #f8f9fa; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .info-label { color: #666; font-size: 14px; margin-bottom: 2px; }
    .info-value { color: #000; font-weight: bold; font-size: 18px; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

# --- HỆ THỐNG XÁC THỰC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="09xxxxxxxx")
        if st.form_submit_button("ĐĂNG NHẬP"):
            try:
                # Đọc dữ liệu, nếu không có tiêu đề sẽ tự đặt tên cột là 0, 1, 2...
                df = pd.read_csv(CSV_URL, dtype=str, header=None)
                target = clean_num(sdt_nhap)
                
                match_row = None
                for _, row in df.iterrows():
                    for val in row.values:
                        if target != "" and target == clean_num(val):
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    st.session_state.auth = True
                    st.session_state.user = {"phone": sdt_nhap, "data": match_row}
                    st.rerun()
                else:
                    st.error(f"❌ Không tìm thấy SĐT {sdt_nhap} trong danh sách.")
            except:
                st.error("⚠️ Lỗi kết nối dữ liệu Sheets.")
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    
    with st.sidebar:
        # Cố gắng tìm một cái tên để chào
        display_name = "Đồng chí"
        for v in u['data'].values():
            if v and not str(v).isdigit() and len(str(v)) > 3:
                display_name = str(v)
                break
        
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {display_name}</h3>", unsafe_allow_html=True)
        menu = ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"]
        if is_admin: menu.append("📊 QUẢN TRỊ")
        choice = st.radio("CHỨC NĂNG", menu)
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if choice == "🏠 Điểm danh":
        st.subheader("📝 Xác nhận dự họp")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], display_name, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success("Đã điểm danh thành công!")
                st.balloons()
            except: st.error("Lỗi gửi dữ liệu.")

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin Đảng viên")
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        # Hiển thị tất cả các giá trị tìm thấy trong hàng
        for idx, value in u['data'].items():
            if pd.notna(value):
                st.markdown(f'<div class="info-label">Thông tin {idx + 1}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">{value}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ QUẢN TRỊ</h2>", unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL)
            st.metric("Số lượt điểm danh", len(df_log))
            st.dataframe(df_log.tail(20), use_container_width=True)
        except: st.info("Chưa có nhật ký điểm danh.")
