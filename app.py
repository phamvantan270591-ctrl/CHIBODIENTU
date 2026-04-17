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
# Link các trang tính
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
CONFIG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CauHinh"

# Link Script xử lý gửi dữ liệu
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ẤP 4", layout="centered", initial_sidebar_state="collapsed")

# --- SIÊU CSS GIAO DIỆN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .header-container {
        background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
        padding: 50px 20px; border-radius: 0 0 40px 40px;
        color: white; text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 10px 25px rgba(211, 47, 47, 0.3);
    }
    .flag-icon { font-size: 60px; margin-bottom: 10px; display: block; }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.06); margin-bottom: 20px; border: 1px solid #eee; }
    .title-red { color: #d32f2f; font-weight: 800; border-left: 5px solid #d32f2f; padding-left: 15px; margin-bottom: 20px; }
    .stButton>button {
        background: linear-gradient(90deg, #d32f2f 0%, #f44336 100%);
        color: white; border-radius: 12px; height: 3.5em; font-weight: 700; width: 100%; border: none; transition: 0.3s;
    }
    .info-box { background: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #e9ecef; margin-bottom: 10px; }
    .stat-card { text-align: center; padding: 15px; border-radius: 15px; color: white; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

def get_data(url):
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("") if r.status_code == 200 else None
    except: return None

# --- KHỞI TẠO BIẾN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

# --- GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.auth:
    st.markdown('<div class="header-container"><span class="flag-icon">🇻🇳</span><h1>CHI BỘ ẤP 4</h1><p>Đảng bộ xã ... - Huyện ...</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP HỆ THỐNG"):
                df_dv = get_data(CSV_URL)
                if df_dv is not None:
                    target = clean_num(sdt)
                    match = next((r.to_dict() for _, r in df_dv.iterrows() if any(target == clean_num(v) for v in r.values if target != "")), None)
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt, "data": match}
                        st.rerun()
                    else: st.error("❌ Số điện thoại không nằm trong danh sách Chi bộ.")
                else: st.error("⚠️ Lỗi kết nối máy chủ dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="header-container"><h2>Chào Đ/c {ten_dc}</h2><p>Hệ thống thông tin Đảng viên Ấp 4</p></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🇻🇳 CHI BỘ ẤP 4")
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ", "👤 Hồ sơ cá nhân"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    # --- LẤY CẤU HÌNH CUỘC HỌP ---
    conf_df = get_data(CONFIG_URL)
    current_meeting = conf_df.iloc[0, 0] if conf_df is not None and not conf_df.empty else ""
    doc_link = conf_df.iloc[0, 1] if conf_df is not None and len(conf_df.columns) > 1 else ""

    # --- 🏠 TRANG CHỦ (Đảng viên & Admin) ---
    if menu == "🏠 Trang chủ":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">📢 THÔNG BÁO TỪ CHI ỦY</div>', unsafe_allow_html=True)
        if current_meeting:
            st.info(f"📍 **Nội dung:** {current_meeting}")
            if doc_link:
                st.markdown(f"🔗 [**Xem tài liệu cuộc họp tại đây**]({doc_link})")
            
            # Kiểm tra trạng thái điểm danh
            df_log = get_data(LOG_URL)
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
                        status_val = "Có mặt"
                        ly_do = ""
                        # Gửi data
                        requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "NhatKyHop", "values": [datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, status_val, current_meeting, ly_do]}))
                        st.rerun()
                with col2:
                    if st.button("❌ BÁO VẮNG"):
                        st.session_state.reporting_absent = True
                
                if st.session_state.get('reporting_absent'):
                    ly_do = st.text_input("Lý do vắng mặt:", placeholder="Ghi rõ lý do...")
                    if st.button("XÁC NHẬN VẮNG"):
                        requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "NhatKyHop", "values": [datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, "Vắng", current_meeting, ly_do]}))
                        st.session_state.reporting_absent = False
                        st.rerun()
        else:
            st.write("Hiện chưa có thông báo cuộc họp mới.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 👤 HỒ SƠ CÁ NHÂN ---
    elif menu == "👤 Hồ sơ cá nhân":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">THÔNG TIN ĐẢNG VIÊN</div>', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-box"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 📊 QUẢN TRỊ (Chỉ Admin) ---
    elif menu == "📊 Quản trị":
        # Phần 1: Tạo cuộc họp
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">⚙️ ĐIỀU HÀNH CUỘC HỌP</div>', unsafe_allow_html=True)
        new_m = st.text_input("Tên cuộc họp mới:", value=current_meeting)
        new_d = st.text_input("Link ảnh/tài liệu (Google Drive/Photo):", value=doc_link)
        if st.button("📢 PHÁT HÀNH THÔNG BÁO MỚI"):
            requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "CauHinh", "values": [new_m, new_d], "method": "update_config"}))
            st.success("Đã cập nhật!"); time.sleep(1); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Phần 2: Thống kê
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">📈 THỐNG KÊ ĐIỂM DANH</div>', unsafe_allow_html=True)
        df_dv = get_data(CSV_URL)
        df_log = get_data(LOG_URL)
        
        if df_dv is not None and df_log is not None:
            total_dv = len(df_dv)
            # Lọc những người đã phản hồi cho cuộc họp hiện tại
            responded_df = df_log[df_log.iloc[:, 4] == current_meeting]
            attended = len(responded_df[responded_df.iloc[:, 3] == "Có mặt"])
            absent = len(responded_df[responded_df.iloc[:, 3] == "Vắng"])
            not_yet = total_dv - (attended + absent)

            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="stat-card" style="background:#2e7d32"><b>CÓ MẶT</b><br><h2>{attended}</h2></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-card" style="background:#d32f2f"><b>BÁO VẮNG</b><br><h2>{absent}</h2></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-card" style="background:#f9a825"><b>CHƯA BÁO</b><br><h2>{not_yet}</h2></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.write("**Chi tiết phản hồi:**")
            st.dataframe(responded_df.iloc[:, [0, 2, 3, 5]], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
