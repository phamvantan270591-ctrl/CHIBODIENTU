import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import io
import time

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
CONFIG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CauHinh"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ẤP 4", layout="centered", initial_sidebar_state="collapsed")

# --- CSS GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .header-container {
        background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
        padding: 40px 20px; border-radius: 0 0 35px 35px;
        color: white; text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 10px 20px rgba(211, 47, 47, 0.2);
    }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .title-red { color: #d32f2f; font-weight: 800; border-left: 5px solid #d32f2f; padding-left: 15px; margin-bottom: 15px; }
    .stButton>button { background: #d32f2f; color: white; border-radius: 12px; font-weight: 700; width: 100%; border: none; height: 3.5em; }
    .info-box { background: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 4px solid #d32f2f; margin-bottom: 10px; }
    .stat-card { text-align: center; padding: 15px; border-radius: 15px; color: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

def get_data_utf8(url):
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.text), dtype=str, encoding='utf-8').fillna("")
        return None
    except: return None

# --- KHỞI TẠO ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

# --- TRANG ĐĂNG NHẬP ---
if not st.session_state.auth:
    st.markdown('<div class="header-container"><h1>🇻🇳 CHI BỘ ẤP 4</h1><p>Hệ thống quản lý Đảng viên số</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt = st.text_input("📱 Nhập số điện thoại:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                df_dv = get_data_utf8(CSV_URL)
                if df_dv is not None:
                    target = clean_num(sdt)
                    match = None
                    for _, row in df_dv.iterrows():
                        if any(target == clean_num(v) for v in row.values if target != ""):
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt, "data": match}
                        st.rerun()
                    else: st.error("❌ Số điện thoại không đúng.")
                else: st.error("⚠️ Lỗi kết nối dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = "Đồng chí"
    for v in u['data'].values():
        if v and not str(v).isdigit() and len(str(v)) > 2:
            ten_dc = str(v); break

    st.markdown(f'<div class="header-container"><h2>Chào Đ/c {ten_dc}</h2></div>', unsafe_allow_html=True)

    with st.sidebar:
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ", "👤 Hồ sơ cá nhân"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    # Lấy cấu hình cuộc họp (đã xử lý tiếng Việt)
    conf_df = get_data_utf8(CONFIG_URL)
    current_meeting = conf_df.iloc[0, 0] if conf_df is not None and not conf_df.empty else ""
    doc_link = conf_df.iloc[0, 1] if conf_df is not None and len(conf_df.columns) > 1 else ""

    # --- 🏠 TRANG CHỦ: ĐIỂM DANH & BÁO VẮNG ---
    if menu == "🏠 Trang chủ":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">📍 THÔNG TIN CUỘC HỌP</div>', unsafe_allow_html=True)
        
        if current_meeting:
            st.info(f"**Nội dung:** {current_meeting}")
            if doc_link:
                st.markdown(f"🔗 [**Tài liệu kèm theo**]({doc_link})")
            
            # Kiểm tra xem đã điểm danh chưa
            df_log = get_data_utf8(LOG_URL)
            my_status = None
            if df_log is not None and not df_log.empty:
                check = df_log[(df_log.iloc[:, 1].apply(clean_num) == clean_num(u['phone'])) & (df_log.iloc[:, 4] == current_meeting)]
                if not check.empty:
                    my_status = check.iloc[0, 3]

            if my_status:
                st.success(f"✅ Đồng chí đã báo: **{my_status}**")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ CÓ MẶT"):
                        payload = {"sheetName": "NhatKyHop", "values": [datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, "Có mặt", current_meeting, ""]}
                        requests.post(SCRIPT_URL, data=json.dumps(payload))
                        st.success("Đã điểm danh!"); time.sleep(1); st.rerun()
                with col2:
                    if st.button("❌ BÁO VẮNG"):
                        st.session_state.absent_mode = True
                
                if st.session_state.get('absent_mode'):
                    reason = st.text_input("Lý do vắng mặt:", placeholder="Nhập lý do...")
                    if st.button("XÁC NHẬN VẮNG"):
                        payload = {"sheetName": "NhatKyHop", "values": [datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, "Vắng", current_meeting, reason]}
                        requests.post(SCRIPT_URL, data=json.dumps(payload))
                        st.session_state.absent_mode = False
                        st.success("Đã gửi báo vắng!"); time.sleep(1); st.rerun()
        else:
            st.write("Hiện chưa có thông báo họp mới.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 👤 HỒ SƠ ---
    elif menu == "👤 Hồ sơ cá nhân":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">THÔNG TIN ĐẢNG VIÊN</div>', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-box"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 📊 QUẢN TRỊ ---
    elif menu == "📊 Quản trị":
        # Tạo họp mới
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">⚙️ QUẢN LÝ CUỘC HỌP</div>', unsafe_allow_html=True)
        m_name = st.text_input("Tên cuộc họp:", value=current_meeting)
        m_doc = st.text_input("Link tài liệu:", value=doc_link)
        if st.button("📢 CẬP NHẬT THÔNG BÁO"):
            requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "CauHinh", "values": [m_name, m_doc], "method": "update_config"}))
            st.success("Đã cập nhật!"); time.sleep(1); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Thống kê
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">📊 THỐNG KÊ ĐIỂM DANH</div>', unsafe_allow_html=True)
        df_dv = get_data_utf8(CSV_URL)
        df_log = get_data_utf8(LOG_URL)
        if df_dv is not None and df_log is not None:
            resp_df = df_log[df_log.iloc[:, 4] == current_meeting]
            attended = len(resp_df[resp_df.iloc[:, 3] == "Có mặt"])
            absent = len(resp_df[resp_df.iloc[:, 3] == "Vắng"])
            total = len(df_dv)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="stat-card" style="background:#2e7d32">CÓ MẶT<br><h3>{attended}</h3></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-card" style="background:#d32f2f">VẮNG<br><h3>{absent}</h3></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-card" style="background:#f9a825">CHƯA BÁO<br><h3>{total-attended-absent}</h3></div>', unsafe_allow_html=True)
            st.dataframe(resp_df.iloc[:, [0, 2, 3, 5]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
