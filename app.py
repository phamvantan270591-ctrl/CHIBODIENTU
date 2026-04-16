import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- GIAO DIỆN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 10px solid #d32f2f; background-color: #f8f9fa; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .info-row { margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
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
                df = pd.read_csv(CSV_URL, dtype=str)
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
        # Lấy tên hiển thị linh hoạt
        display_name = "Đồng chí"
        for k, v in u['data'].items():
            if any(x in str(k).lower() for x in ['họ tên', 'tên', 'hoten']):
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
                st.success("Đã ghi nhận điểm danh!")
                st.balloons()
            except: st.error("Lỗi gửi dữ liệu.")

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin Đảng viên")
        with st.container():
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)
            # Tự động hiển thị TẤT CẢ các cột có dữ liệu trong Sheets
            for key, value in u['data'].items():
                if "Unnamed" not in str(key): # Bỏ qua các cột trống vô danh
                    st.markdown(f"""
                    <div class="info-row">
                        <span style="color: #666; font-size: 14px;">{key}</span><br>
                        <span style="color: #000; font-weight: bold; font-size: 18px;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ QUẢN TRỊ</h2>", unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL)
            st.metric("Số lượt điểm danh", len(df_log))
            st.dataframe(df_log.tail(20), use_container_width=True)
        except: st.info("Chưa có nhật ký điểm danh.")
