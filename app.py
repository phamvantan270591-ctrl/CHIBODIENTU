import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import time

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
def get_url(gid=0, sheet_name=None):
    if sheet_name:
        return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&c={int(time.time())}"
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&c={int(time.time())}"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
    <style>
    .stApp { background: #f0f2f5; }
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
        padding: 30px; border-radius: 0 0 25px 25px; color: white;
        text-align: center; margin: -60px -20px 25px -20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 12px; height: 3.5em;
        font-weight: 700; width: 100%; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background: #b71c1c; transform: scale(1.02); }
    .info-tile {
        background: #f8f9fa; padding: 12px; border-radius: 10px;
        border-left: 5px solid #d32f2f; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

# --- KHỞI TẠO HỆ THỐNG ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header-box"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Nâng cao năng lực lãnh đạo số</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login_form"):
            sdt_in = st.text_input("📱 Nhập số điện thoại:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                try:
                    df = pd.read_csv(get_url(gid=0), dtype=str).fillna("")
                    target = clean_num(sdt_in)
                    match = None
                    for _, row in df.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt_in, "data": match}
                        st.rerun()
                    else: st.error("Số điện thoại không nằm trong danh sách Chi bộ.")
                except: st.error("Không thể kết nối dữ liệu. Vui lòng kiểm tra quyền chia sẻ Sheets.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="header-box"><h2>Chào Đ/c {ten_dc}</h2><p>Hệ thống quản lý trực tuyến</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚡ TIỆN ÍCH")
        menu = st.radio("Chọn chức năng:", ["🏠 Trang chủ", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if menu == "🏠 Trang chủ":
        # KHỐI ĐIỂM DANH
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 Điểm danh dự họp")
        if st.button("XÁC NHẬN CÓ MẶT NGAY"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
                st.success(f"Đã điểm danh lúc: {gio}"); st.balloons()
            except: st.error("Lỗi gửi dữ liệu về hệ thống.")
        st.markdown('</div>', unsafe_allow_html=True)

        # KHỐI HỒ SƠ
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👤 Thông tin cá nhân")
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-tile"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "📊 Quản trị":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🖥️ Báo cáo điểm danh")
        try:
            # Ép đọc dữ liệu mới nhất từ trang NhatKyHop
            df_log = pd.read_csv(get_url(sheet_name="NhatKyHop"), dtype=str)
            if not df_log.empty:
                st.metric("Tổng lượt Đảng viên dự họp", len(df_log))
                st.dataframe(df_log.tail(20), use_container_width=True)
            else:
                st.info("Trang 'NhatKyHop' hiện đang trống.")
        except Exception as e:
            st.warning("⚠️ Chưa tìm thấy dữ liệu điểm danh. Đồng chí hãy đảm bảo đã tạo tab 'NhatKyHop' trong file Sheets.")
        st.markdown('</div>', unsafe_allow_html=True)
