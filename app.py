import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link ép kiểu lấy dữ liệu chuẩn CSV không qua cache
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered", initial_sidebar_state="collapsed")

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
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .info-item { background: #f1f3f5; padding: 15px; border-radius: 12px; border: 1px solid #e9ecef; }
    .info-label { font-size: 12px; color: #6c757d; font-weight: 600; margin-bottom: 5px; }
    .info-value { font-size: 16px; color: #212529; font-weight: 700; }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 15px; height: 3.8em;
        font-weight: 700; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Hàm chuẩn hóa: Xóa sạch mọi thứ, chỉ giữ lại các chữ số"""
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    # Nếu số điện thoại có số 0 ở đầu, ta bỏ đi để so sánh cho dễ (tránh lỗi 09 vs 9)
    return s.lstrip('0')

# --- LOGIC XỬ LÝ ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="main-header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Hệ thống quản lý Đảng viên 4.0</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    with st.form("login"):
        sdt_input = st.text_input("📱 Nhập số điện thoại đăng ký:", placeholder="Ví dụ: 0927...")
        if st.form_submit_button("ĐĂNG NHẬP NGAY"):
            try:
                # Đọc dữ liệu và ÉP KIỂU STRING cho tất cả để không bị mất số 0
                df = pd.read_csv(CSV_URL, dtype=str).fillna("")
                target = clean_num(sdt_input)
                
                match_row = None
                if target != "":
                    for _, row in df.iterrows():
                        # Kiểm tra từng ô trong hàng, nếu có ô nào chứa số điện thoại khớp đuôi
                        if any(target == clean_num(val) for val in row.values):
                            match_row = row.to_dict()
                            break
                
                if match_row:
                    st.session_state.auth = True
                    st.session_state.user = {"phone": sdt_input, "data": match_row}
                    st.rerun()
                else:
                    st.error("❌ Không tìm thấy thông tin đồng chí. Vui lòng kiểm tra lại số điện thoại trong file Sheets.")
            except Exception as e:
                st.error(f"⚠️ Lỗi kết nối: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    # Tìm tên trong dữ liệu hàng
    ten_dc = "Đồng chí"
    for v in u['data'].values():
        if v and not str(v).isdigit() and len(str(v)) > 2:
            ten_dc = str(v)
            break

    st.markdown(f'<div class="main-header"><h3>Chào Đ/c {ten_dc}</h3><p>Chi bộ chúc đồng chí một ngày làm việc hiệu quả</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.title("DANH MỤC")
        menu = st.radio("Chức năng:", ["🏠 Dashboard", "📊 Quản trị"] if is_admin else ["🏠 Dashboard"])
        if st.button("🚪 Thoát hệ thống"):
            st.session_state.auth = False
            st.rerun()

    if "Dashboard" in menu:
        # THÀNH PHẦN 1: ĐIỂM DANH
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#d32f2f; margin-top:0;">📍 ĐIỂM DANH DỰ HỌP</h4>', unsafe_allow_html=True)
        if st.button("XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"Đã ghi nhận điểm danh lúc {gio}")
                st.balloons()
            except: st.error("Lỗi gửi dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)

        # THÀNH PHẦN 2: HỒ SƠ
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#212529; margin-top:0;">👤 THÔNG TIN CHI TIẾT</h4>', unsafe_allow_html=True)
        st.markdown('<div class="info-grid">', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'''
                    <div class="info-item">
                        <div class="info-label">{k}</div>
                        <div class="info-value">{v}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif "Quản trị" in menu:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🖥️ Báo cáo Chi bộ")
        try:
            df_log = pd.read_csv(LOG_URL)
            st.metric("Tổng lượt điểm danh", len(df_log))
            st.dataframe(df_log.tail(15), use_container_width=True)
        except: st.info("Đang cập nhật nhật ký...")
        st.markdown('</div>', unsafe_allow_html=True)
