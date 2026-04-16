import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered", initial_sidebar_state="collapsed")

# --- SIÊU CSS: GIAO DIỆN PREMIUM ---
st.markdown("""
    <style>
    /* Tổng thể */
    .stApp { background: linear-gradient(180deg, #f0f2f5 0%, #ffffff 100%); }
    
    /* Header Header */
    .main-header {
        background: linear-gradient(90deg, #d32f2f 0%, #b71c1c 100%);
        padding: 30px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin: -60px -20px 30px -20px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }

    /* Thẻ nội dung (Content Cards) */
    .custom-card {
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05); margin-bottom: 20px;
        border: 1px solid rgba(0,0,0,0.02);
    }
    
    .card-title {
        font-size: 18px; font-weight: 700; color: #1a1a1a;
        margin-bottom: 15px; display: flex; align-items: center; gap: 10px;
    }

    /* Grid thông tin hồ sơ */
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .info-item {
        background: #f8f9fa; padding: 12px; border-radius: 12px;
        border: 1px solid #eee;
    }
    .info-label { font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600; }
    .info-value { font-size: 15px; color: #2d3748; font-weight: 700; }

    /* Nút bấm Premium */
    .stButton>button {
        background: linear-gradient(90deg, #d32f2f 0%, #f44336 100%);
        color: white; border: none; padding: 15px 25px;
        border-radius: 15px; font-weight: 700; font-size: 16px;
        width: 100%; transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.2);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(211, 47, 47, 0.4); }
    
    /* Sidebar tinh chỉnh */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

# --- LOGIC XÁC THỰC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="main-header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1><p>Vững bước dưới cờ Đảng</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt = st.text_input("📱 Số điện thoại Đảng viên:", placeholder="Nhập để tiếp tục...")
            if st.form_submit_button("ĐĂNG NHẬP HỆ THỐNG"):
                try:
                    df = pd.read_csv(CSV_URL, dtype=str)
                    target = clean_num(sdt)
                    match_row = None
                    for _, row in df.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match_row = row.to_dict(); break
                    if match_row:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt, "data": match_row}
                        st.rerun()
                    else: st.error("Tài khoản không tồn tại trên hệ thống.")
                except: st.error("Lỗi kết nối máy chủ dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 3), "Đồng chí")

    # Header chào mừng
    st.markdown(f'<div class="main-header"><h3>Chào Đ/c {ten_dc}</h3><p>Hôm nay là {datetime.now().strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("⚡ TIỆN ÍCH")
        menu = st.radio("Chức năng:", ["🏠 Dashboard", "📊 Quản trị"] if is_admin else ["🏠 Dashboard"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if "Dashboard" in menu:
        # 1. KHỐI ĐIỂM DANH (Ưu tiên số 1)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📍 ĐIỂM DANH SINH HOẠT</div>', unsafe_allow_html=True)
        if st.button("BẤM ĐỂ XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"Ghi nhận lúc: {gio}"); st.balloons()
            except: st.error("Lỗi đồng bộ.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. KHỐI TÀI LIỆU (Dạng danh sách đẹp)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📖 TÀI LIỆU NỘI BỘ</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown("📄 **Nghị quyết tháng**")
        col2.markdown("📄 **Báo cáo chuyên đề**")
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. KHỐI HỒ SƠ (Dạng Grid chuyên nghiệp)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👤 HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-grid">', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if pd.notna(v) and "Unnamed" not in str(k):
                st.markdown(f'''
                    <div class="info-item">
                        <div class="info-label">{k}</div>
                        <div class="info-value">{v}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif "Quản trị" in menu:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🖥️ TRUNG TÂM ĐIỀU HÀNH</div>', unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL)
            c1, c2 = st.columns(2)
            c1.metric("Lượt điểm danh", len(df_log))
            c2.metric("Trạng thái", "Ổn định")
            st.dataframe(df_log.tail(10), use_container_width=True)
        except: st.info("Hệ thống đang sẵn sàng.")
        st.markdown('</div>', unsafe_allow_html=True)
