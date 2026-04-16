import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import time

# --- CẤU HÌNH HỆ THỐNG (GIỮ NGUYÊN) ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
def get_url(gid=0, sheet_name=None):
    t = int(time.time())
    if sheet_name:
        return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&c={t}"
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&c={t}"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered", initial_sidebar_state="collapsed")

# --- SIÊU CSS: GIAO DIỆN CHI BỘ 4.0 ---
st.markdown("""
    <style>
    /* Nền và phông chữ */
    .stApp { background-color: #f0f2f5; }
    
    /* Header đỏ rực rỡ */
    .main-header {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 45px 20px; border-radius: 0 0 40px 40px;
        color: white; text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 10px 20px rgba(211, 47, 47, 0.2);
    }
    .main-header h1 { font-size: 26px; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
    .main-header p { font-size: 14px; opacity: 0.9; font-weight: 300; }

    /* Khối nội dung trắng (Cards) */
    .custom-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* Tiêu đề mục */
    .title-box {
        border-left: 6px solid #d32f2f; padding-left: 15px;
        margin-bottom: 20px; color: #1a1a1a; font-weight: 700; font-size: 19px;
    }

    /* Các hàng thông tin hồ sơ */
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .info-tile {
        background: #f8fafc; padding: 15px; border-radius: 15px;
        border: 1px solid #edf2f7; transition: 0.3s;
    }
    .info-tile:hover { background: #fff; border-color: #d32f2f; box-shadow: 0 5px 10px rgba(0,0,0,0.05); }
    .info-label { font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600; }
    .info-value { font-size: 15px; color: #1a202c; font-weight: 700; margin-top: 3px; }

    /* Nút bấm đỏ đặc trưng */
    .stButton>button {
        background: linear-gradient(90deg, #d32f2f 0%, #ff5252 100%);
        color: white; border-radius: 15px; height: 3.8em; font-weight: 700;
        width: 100%; border: none; font-size: 16px; transition: 0.4s;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(211, 47, 47, 0.4); }

    /* Tab và Tài liệu */
    .doc-item {
        display: flex; align-items: center; padding: 12px;
        background: #fff; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid #eee; gap: 10px; cursor: pointer;
    }
    .doc-icon { font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

# --- HỆ THỐNG XÁC THỰC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="main-header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Ứng dụng Sinh hoạt Đảng thông minh</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="title-box">ĐĂNG NHẬP</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            sdt_in = st.text_input("📱 Nhập số điện thoại của đồng chí:", placeholder="09xxxxxxxx")
            if st.form_submit_button("VÀO HỆ THỐNG"):
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
                    else: st.error("❌ Không tìm thấy SĐT này trong danh sách.")
                except: st.error("⚠️ Lỗi kết nối Sheets. Kiểm tra lại quyền Chia sẻ.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="main-header"><h1>CHÀO Đ/C {ten_dc.upper()}</h1><p>{datetime.now().strftime("Ngày %d tháng %m năm %Y")}</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h2 style='color:#d32f2f'>⚡ CÔNG CỤ</h2>", unsafe_allow_html=True)
        menu = st.radio("Chức năng chính:", ["🏠 Bàn làm việc", "📊 Quản trị viên"] if is_admin else ["🏠 Bàn làm việc"])
        st.write("---")
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if menu == "🏠 Bàn làm việc":
        # KHỐI 1: ĐIỂM DANH (Thiết kế nổi bật nhất)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="title-box">📍 ĐIỂM DANH DỰ HỌP</div>', unsafe_allow_html=True)
        if st.button("XÁC NHẬN CÓ MẶT TẠI BUỔI HỌP"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"✅ Đã ghi nhận lúc {gio}")
                st.balloons()
            except: st.error("Lỗi gửi dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)

        # KHỐI 2: TÀI LIỆU (Thiết kế dạng danh sách App)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="title-box">📂 TÀI LIỆU SINH HOẠT</div>', unsafe_allow_html=True)
        docs = [("📄", "Nghị quyết Chi bộ tháng này"), ("📜", "Hướng dẫn học tập chuyên đề"), ("📋", "Mẫu bản kiểm điểm Đảng viên")]
        for icon, name in docs:
            st.markdown(f'''
                <div class="doc-item">
                    <span class="doc-icon">{icon}</span>
                    <span style="font-weight:500;">{name}</span>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # KHỐI 3: HỒ SƠ (Thiết kế dạng Grid 2 cột)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="title-box">👤 HỒ SƠ CÁ NHÂN</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-grid">', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'''
                    <div class="info-tile">
                        <div class="info-label">{k}</div>
                        <div class="info-value">{v}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "📊 Quản trị viên":
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="title-box">🖥️ TRUNG TÂM ĐIỀU HÀNH</div>', unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(get_url(sheet_name="NhatKyHop"), dtype=str)
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng lượt", len(df_log))
            c2.metric("Ngày họp", datetime.now().strftime("%d/%m"))
            c3.metric("Trạng thái", "Mở")
            st.write("---")
            st.dataframe(df_log.tail(15), use_container_width=True)
        except: st.info("Hệ thống quản trị đang chờ dữ liệu điểm danh đầu tiên.")
        st.markdown('</div>', unsafe_allow_html=True)
