import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime
import pytz

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Phương thức đọc dữ liệu trực tiếp từ Google Export
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered")

# --- CSS GIAO DIỆN KHỐI ---
st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    .header { background: #d32f2f; padding: 30px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin: -60px -20px 20px -20px; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stButton>button { background: #d32f2f; color: white; border-radius: 10px; width: 100%; font-weight: bold; height: 3.5em; border: none; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

# --- LOGIC ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt_in = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                try:
                    # Thêm tham số t để phá cache
                    df = pd.read_csv(f"{CSV_URL}&t={int(time.time())}", dtype=str).fillna("")
                    target = clean_num(sdt_in)
                    match = None
                    for _, row in df.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt_in, "data": match}
                        st.rerun()
                    else: st.error("❌ Số điện thoại không khớp với danh sách.")
                except Exception as e:
                    st.error("⚠️ LỖI KẾT NỐI: Đồng chí hãy nhấn 'Chia sẻ' Sheets và chọn 'Bất kỳ ai có liên kết' nhé!")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="header"><h3>Chào Đ/c {ten_dc}</h3></div>', unsafe_allow_html=True)

    # --- MENU TRANG CHỦ ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📍 Điểm danh họp")
    if st.button("XÁC NHẬN CÓ MẶT"):
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
        try:
            requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}))
            st.success(f"Thành công: {gio}"); st.balloons()
        except: st.error("Lỗi gửi dữ liệu.")
    st.markdown('</div>', unsafe_allow_html=True)

    if is_admin:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Quản trị (Chỉ Admin)")
        if st.button("TẢI DỮ LIỆU ĐIỂM DANH"):
            try:
                df_log = pd.read_csv(f"{LOG_URL}&t={time.time()}", dtype=str)
                st.dataframe(df_log.tail(10), use_container_width=True)
            except: st.warning("Chưa có nhật ký điểm danh.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Đăng xuất"):
        st.session_state.auth = False; st.rerun()
