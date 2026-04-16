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
# Trang tính dùng để Admin nhập tên nội dung họp hiện tại
CONFIG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CauHinh"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header { background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%); padding: 35px 20px; border-radius: 0 0 30px 30px; color: white; text-align: center; margin: -65px -20px 30px -20px; }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .status-badge { padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; background: #e8f5e9; color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    if pd.isna(p) or p == "": return ""
    return ''.join(filter(str.isdigit, str(p))).lstrip('0')

def get_data_secure(url):
    try:
        response = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text), dtype=str).fillna("")
        return None
    except: return None

# --- LOGIC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header"><h1>🇻🇳 CHI BỘ ĐIỆN TỬ</h1></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt_in = st.text_input("📱 Số điện thoại Đảng viên:", placeholder="Nhập số của đồng chí...")
            if st.form_submit_button("ĐĂNG NHẬP"):
                df = get_data_secure(CSV_URL)
                if df is not None:
                    target = clean_num(sdt_in)
                    match = next((r.to_dict() for _, r in df.iterrows() if any(target == clean_num(v) for v in r.values if target != "")), None)
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt_in, "data": match}
                        st.rerun()
                    else: st.error("Số điện thoại không có trong danh sách.")
                else: st.error("Lỗi kết nối dữ liệu Sheets.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    ten_dc = next((str(v) for v in u['data'].values() if v and not str(v).isdigit() and len(str(v)) > 2), "Đồng chí")

    st.markdown(f'<div class="header"><h3>Chào Đ/c {ten_dc}</h3></div>', unsafe_allow_html=True)

    with st.sidebar:
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    if menu == "🏠 Trang chủ":
        # 1. Lấy thông tin cấu hình từ Admin
        conf_df = get_data_secure(CONFIG_URL)
        current_event = conf_df.iloc[0, 0] if conf_df is not None and not conf_df.empty else "Chưa có nội dung"
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 ĐIỂM DANH")
        st.info(f"Nội dung hiện tại: **{current_event}**")

        if current_event == "Chưa có nội dung" or current_event == "":
            st.warning("Hiện tại chưa có thông báo điểm danh mới từ Quản trị viên.")
        else:
            # 2. Kiểm tra xem người này đã điểm danh nội dung này chưa
            df_log = get_data_secure(LOG_URL)
            already_done = False
            if df_log is not None and not df_log.empty:
                # Kiểm tra cột SĐT và Cột Nội dung (Giả sử cột Nội dung là cột cuối cùng hoặc cột thứ 5)
                # Ta lọc theo SĐT và Nội dung họp
                check = df_log[(df_log.iloc[:, 1].apply(clean_num) == clean_num(u['phone'])) & (df_log.iloc[:, 4] == current_event)]
                if not check.empty:
                    already_done = True

            if already_done:
                st.success("✅ Đồng chí đã hoàn thành điểm danh cho nội dung này.")
            else:
                if st.button("XÁC NHẬN CÓ MẶT NGAY"):
                    tz = pytz.timezone('Asia/Ho_Chi_Minh')
                    gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
                    # Gửi thêm nội dung cuộc họp để khóa
                    payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], ten_dc, "Có mặt", current_event]}
                    try:
                        requests.post(SCRIPT_URL, data=json.dumps(payload))
                        st.success("Điểm danh thành công!"); st.balloons()
                        time.sleep(2)
                        st.rerun()
                    except: st.error("Lỗi gửi dữ liệu.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "📊 Quản trị":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚙️ ĐIỀU HÀNH NỘI DUNG")
        new_event = st.text_input("Nhập nội dung họp mới (Ví dụ: Họp chi bộ 03/04):")
        if st.button("📢 CẬP NHẬT THÔNG BÁO MỚI"):
            # Gửi tên cuộc họp vào trang CauHinh (O A1)
            payload = {"sheetName": "CauHinh", "values": [new_event], "method": "update"} 
            # Lưu ý: Đồng chí cần sửa Script Google App để hỗ trợ xóa/ghi đè ô A1
            st.success("Đã cập nhật nội dung mới. Đảng viên bây giờ có thể điểm danh lần đầu.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 DANH SÁCH ĐIỂM DANH")
        df_log = get_data_secure(LOG_URL)
        if df_log is not None:
            st.dataframe(df_log, use_container_width=True)
