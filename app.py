import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Lấy dữ liệu trang đầu tiên (Danh sách Đảng viên)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Link Script để ghi dữ liệu
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại quản trị viên (Của đồng chí)
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

def clean_num(p):
    return ''.join(filter(str.isdigit, str(p)))

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except: return False

# --- KIỂM TRA ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.title("🏛️ CHI BỘ ĐIỆN TỬ")
    st.subheader("Xác thực Đảng viên")
    with st.form("login_form"):
        sdt_nhap = st.text_input("Nhập số điện thoại của đồng chí:").strip()
        if st.form_submit_button("VÀO HỆ THỐNG"):
            try:
                df = pd.read_csv(CSV_URL)
                sdt_target = clean_num(sdt_nhap)
                match = None
                for _, row in df.iterrows():
                    for cell in row:
                        if sdt_target != "" and sdt_target in clean_num(cell):
                            match = row.to_dict()
                            break
                    if match: break
                
                if match:
                    st.session_state.auth = True
                    # Lấy Họ tên từ cột đầu tiên của file Sheets
                    st.session_state.user = {"name": str(list(match.values())[0]), "phone": sdt_nhap}
                    st.rerun()
                else:
                    st.error(f"Không tìm thấy số {sdt_nhap} trong danh sách!")
            except:
                st.error("Lỗi kết nối dữ liệu!")
else:
    user = st.session_state.user
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    # --- THANH MENU BÊN TRÁI ---
    st.sidebar.markdown(f"### Chào đồng chí:\n**{user['name']}**")
    menu = ["🏠 Điểm danh họp", "📖 Tài liệu sinh hoạt", "👤 Hồ sơ cá nhân"]
    if is_admin:
        menu.append("📊 QUẢN TRỊ CHI BỘ")
