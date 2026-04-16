import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import io
import time

# --- CẤU HÌNH CỐ ĐỊNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link xuất bản CSV trực tiếp (Đường này là chắc chắn nhất)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered", initial_sidebar_state="collapsed")

# --- CSS CAO CẤP ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header { background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%); padding: 40px 20px; border-radius: 0 0 30px 30px; color: white; text-align: center; margin: -65px -20px 30px -20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #edf2f7; }
    .stButton>button { background: #d32f2f; color: white; border-radius: 12px; font-weight: 700; width: 100%; height: 3.5em; border: none; transition: 0.3s; }
    .stButton>button:hover { background: #b71c1c; transform: translateY(-2px); }
    .info-tile { background: #f1f5f9; padding: 12px; border-radius: 10px; border-left: 4px solid #d32f2f; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

def get_data_secure(url):
    """Hàm tải dữ liệu bằng requests để tránh lỗi chặn link trực tiếp"""
    try:
        response = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text), dtype=str).fillna("")
        return None
    except:
        return None

# --- LOGIC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Ứng dụng quản lý sinh hoạt Đảng viên</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login_form"):
            sdt_in = st.text_input("📱 Số điện thoại của đồng chí:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                df = get_data_secure(CSV_URL)
                if df is not None:
                    target = clean_num(sdt_in)
                    match = None
                    for _, row in df.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt_in, "data": match}
                        st.rerun()
                    else: st.error("❌ Số điện thoại không có trong danh sách.")
                else: st.error("⚠️ Không thể lấy dữ liệu. Hãy đảm bảo Sheets đã chọn 'Bất kỳ ai có liên kết đều có thể xem'.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="header"><h1>CHÀO Đ/C {ten_dc.upper()}</h1></div>', unsafe_allow_html=True)

    with st.sidebar:
        menu = st.radio("Menu:", ["🏠 Trang chủ", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if menu == "🏠 Trang chủ":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 Điểm danh họp")
        if st.button("XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            try:
                requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}))
                st.success("Đã ghi nhận!"); st.balloons()
            except: st.error("Lỗi gửi điểm danh.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👤 Hồ sơ")
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-tile"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "📊 Quản trị":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        df_log = get_data_secure(LOG_URL)
        if df_log is not None:
            st.metric("Lượt dự họp", len(df_log))
            st.dataframe(df_log.tail(20), use_container_width=True)
        else: st.warning("Chưa có dữ liệu nhật ký.")
        st.markdown('</div>', unsafe_allow_html=True)
