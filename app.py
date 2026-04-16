import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại Admin chuẩn
ADMIN_PHONE_RAW = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .stMetric { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 8px solid #d32f2f; background-color: #f1f1f1; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Lấy 9 chữ số cuối cùng để so khớp chính xác"""
    p_str = ''.join(filter(str.isdigit, str(p)))
    return p_str[-9:] if len(p_str) >= 9 else p_str

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
        return True
    except: return False

# --- ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_data = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:")
        if st.form_submit_button("ĐĂNG NHẬP"):
            try:
                df = pd.read_csv(CSV_URL)
                sdt_target = clean_num(sdt_nhap)
                match_row = None
                for _, row in df.iterrows():
                    for cell in row:
                        if sdt_target != "" and sdt_target == clean_num(cell):
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    ten = "Đồng chí"
                    for k, v in match_row.items():
                        if any(x in k.lower() for x in ['họ tên', 'hoten', 'tên']):
                            ten = str(v)
                            break
                    st.session_state.auth = True
                    st.session_state.user_data = {"name": ten, "phone": sdt_nhap}
                    st.rerun()
                else: st.error("Không tìm thấy thông tin!")
            except: st.error("Lỗi kết nối dữ liệu!")
else:
    user = st.session_state.user_data
    # SO KHỚP ADMIN CHÍNH XÁC (Lấy 9 số cuối)
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE_RAW)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {user['name']}</h3>", unsafe_allow_html=True)
        # Hiển thị Menu dựa trên quyền
        menu_options = ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"]
        if is_admin:
            menu_options.append("📊 QUẢN TRỊ CHI BỘ")
        
        choice = st.sidebar.radio("CHỨC NĂNG", menu_options)
        if st.sidebar.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if choice == "🏠 Điểm danh":
        st.subheader("📝 Xác nhận dự họp")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [gio, user['phone'], user['name'], "Có mặt"]):
                st.success(f"Đã điểm danh thành công!")
                st.balloons()

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin cá nhân")
        st.markdown(f"<div class='profile-card'><b>Họ và tên:</b> {user['name']}<br><b>SĐT:</b> {user['phone']}<br><b>Quyền hạn:</b> {'Quản trị viên' if is_admin else 'Đảng viên'}</div>", unsafe_allow_html=True)

    elif choice == "📊 QUẢN TRỊ CHI BỘ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ BẢNG ĐIỀU HÀNH</h2>", unsafe_allow_html=True)
        try:
            df_ds = pd.read_csv(CSV_URL)
            df_log = pd.read_csv(LOG_URL)
            
            t_tong = len(df_ds)
            t_co_mat = df_log[df_log.iloc[:, 3] == "Có mặt"].iloc[:, 1].astype(str).apply(clean_num).nunique()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng số", t_tong)
            c2.metric("Đã có mặt", t_co_mat)
            c3.metric("Vắng", t_tong - t_co_mat)
            
            st.write("---")
            st.subheader("📋 Nhật ký điểm danh mới nhất")
            st.dataframe(df_log.tail(15), use_container_width=True)
        except:
            st.info("Chưa có dữ liệu điểm danh trong trang 'NhatKyHop'.")
