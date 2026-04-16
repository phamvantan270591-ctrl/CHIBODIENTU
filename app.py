import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import time

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Thêm tham số thời gian thực vào URL để phá bộ nhớ đệm (Cache Busting)
def get_csv_url(gid=0):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&cache={int(time.time())}"

LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    .main-header {
        background: linear-gradient(90deg, #d32f2f 0%, #b71c1c 100%);
        padding: 40px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin: -60px -20px 30px -20px;
    }
    .custom-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 12px; height: 3.5em;
        font-weight: 700; width: 100%; border: none;
    }
    .info-item { background: #f1f3f5; padding: 15px; border-radius: 12px; border: 1px solid #e9ecef; margin-bottom:10px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Xóa sạch ký tự lạ, giữ lại số, lột bỏ số 0 đầu tiên"""
    if pd.isna(p) or p == "": return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="main-header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Hệ thống quản lý Đảng viên 4.0</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    with st.form("login"):
        sdt_input = st.text_input("📱 Nhập số điện thoại:", placeholder="Ví dụ: 0927...")
        submitted = st.form_submit_button("ĐĂNG NHẬP")
        
        if submitted:
            try:
                # ÉP BUỘC đọc dữ liệu mới nhất
                df = pd.read_csv(get_csv_url(), dtype=str).fillna("")
                target = clean_num(sdt_input)
                
                match_row = None
                # Quét mọi ô trong bảng để tìm số khớp
                for _, row in df.iterrows():
                    for val in row.values:
                        if target != "" and clean_num(val) == target:
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    st.session_state.auth = True
                    st.session_state.user = {"phone": sdt_input, "data": match_row}
                    st.rerun()
                else:
                    st.error(f"❌ Không tìm thấy SĐT '{sdt_input}' trong file.")
                    with st.expander("Gợi ý sửa lỗi"):
                        st.write("1. Hãy chắc chắn số này đã được nhập vào file Sheets.")
                        st.write("2. Đảm bảo file Sheets đã ở chế độ 'Bất kỳ ai có liên kết đều có thể xem'.")
            except Exception as e:
                st.error("Lỗi kết nối máy chủ Google.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="main-header"><h3>Chào Đ/c {ten_dc}</h3><p>Hệ thống đã sẵn sàng</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.title("DANH MỤC")
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if "Trang chủ" in menu:
        # KHỐI ĐIỂM DANH
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#d32f2f; margin-top:0;">📍 ĐIỂM DANH</h4>', unsafe_allow_html=True)
        if st.button("XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"Ghi nhận: {gio}"); st.balloons()
            except: st.error("Lỗi đồng bộ.")
        st.markdown('</div>', unsafe_allow_html=True)

        # KHỐI HỒ SƠ
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#212529; margin-top:0;">👤 HỒ SƠ CÁ NHÂN</h4>', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-item"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif "Quản trị" in menu:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL + f"&c={time.time()}")
            st.metric("Lượt điểm danh", len(df_log))
            st.dataframe(df_log.tail(15), use_container_width=True)
        except: st.info("Đang tải dữ liệu...")
        st.markdown('</div>', unsafe_allow_html=True)
