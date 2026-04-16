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

# --- CSS THIẾT KẾ KHỐI (MODERN UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    /* Khối tổng quát */
    .main-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    /* Tiêu đề khối */
    .section-title {
        color: #d32f2f;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    /* Dòng thông tin trong hồ sơ */
    .info-box {
        background: #f9f9f9;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #d32f2f;
    }
    .info-label { font-size: 12px; color: #666; text-transform: uppercase; }
    .info-value { font-size: 16px; color: #222; font-weight: 600; }
    
    /* Nút bấm đỏ đặc trưng */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #d32f2f; color: white; font-weight: bold;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #b71c1c; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

# --- XÁC THỰC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f; margin-top: 50px;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Đăng nhập để tiếp tục</p>", unsafe_allow_html=True)
    with st.container():
        with st.form("login"):
            sdt_nhap = st.text_input("📱 Số điện thoại:", placeholder="Nhập số của đồng chí...")
            if st.form_submit_button("ĐĂNG NHẬP"):
                try:
                    df = pd.read_csv(CSV_URL, dtype=str)
                    target = clean_num(sdt_nhap)
                    match_row = None
                    for _, row in df.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match_row = row.to_dict()
                            break
                    if match_row:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt_nhap, "data": match_row}
                        st.rerun()
                    else: st.error("Số điện thoại chưa có trong danh sách Chi bộ.")
                except: st.error("Lỗi kết nối dữ liệu.")
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    
    # Tìm tên đồng chí
    ten_dc = "Đồng chí"
    for v in u['data'].values():
        if v and not str(v).isdigit() and len(str(v)) > 3:
            ten_dc = str(v); break

    with st.sidebar:
        st.markdown(f"<h2 style='color: #d32f2f;'>Chào Đ/c {ten_dc}</h2>", unsafe_allow_html=True)
        menu = st.radio("MENU CHÍNH", ["🏠 Trang chủ", "📊 QUẢN TRỊ"] if is_admin else ["🏠 Trang chủ"])
        st.write("---")
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    # --- TRANG CHỦ (KHỐI LẠI ĐẸP MẮT) ---
    if "Trang chủ" in menu:
        # 1. KHỐI ĐIỂM DANH
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📍 ĐIỂM DANH HỌP CHI BỘ</div>', unsafe_allow_html=True)
        st.write("Vui lòng xác nhận sự có mặt của đồng chí trong buổi sinh hoạt hôm nay.")
        if st.button("✅ XÁC NHẬN CÓ MẶT NGAY"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"Thành công! Ghi nhận lúc {gio}")
                st.balloons()
            except: st.error("Gửi dữ liệu thất bại.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. KHỐI TÀI LIỆU
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="color: #1976d2;">📖 TÀI LIỆU SINH HOẠT</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.info("📂 Nghị quyết tháng 04")
        with col2:
            st.info("📂 Chuyên đề học tập")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. KHỐI HỒ SƠ
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="color: #455a64;">👤 HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)
        # Hiển thị dữ liệu dạng hộp
        items = list(u['data'].items())
        for i in range(0, len(items), 2): # Chia làm 2 cột
            c1, c2 = st.columns(2)
            with c1:
                k, v = items[i]
                if pd.notna(v):
                    st.markdown(f'<div class="info-box"><div class="info-label">{k}</div><div class="info-value">{v}</div></div>', unsafe_allow_html=True)
            if i + 1 < len(items):
                with c2:
                    k, v = items[i+1]
                    if pd.notna(v):
                        st.markdown(f'<div class="info-box"><div class="info-label">{k}</div><div class="info-value">{v}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TRANG QUẢN TRỊ ---
    elif "QUẢN TRỊ" in menu:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🖥️ PHÒNG ĐIỀU HÀNH</div>', unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL)
            st.metric("Tổng lượt điểm danh", len(df_log))
            st.dataframe(df_log.tail(10), use_container_width=True)
        except: st.info("Chưa có dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)
