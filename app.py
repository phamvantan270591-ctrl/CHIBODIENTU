import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Lấy dữ liệu dạng công khai
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại của đồng chí
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BO DIEN TU", layout="centered")

# Hàm làm sạch số điện thoại để so khớp
def clean_phone(p):
    p_str = ''.join(filter(str.isdigit, str(p)))
    return p_str[-9:] if len(p_str) >= 9 else p_str

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except: return False

# --- XỬ LÝ ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_info = None

if not st.session_state.auth:
    st.title("🏛️ CHI BO DIEN TU")
    st.subheader("Xác thực Đảng viên")
    
    with st.form("login_form"):
        sdt_nhap = st.text_input("Nhập số điện thoại của đồng chí:").strip()
        submit = st.form_submit_button("VÀO HỆ THỐNG")
        
        if submit:
            if not sdt_nhap:
                st.warning("Vui lòng nhập số điện thoại!")
            else:
                try:
                    # Đọc dữ liệu từ file Sheets
                    df = pd.read_csv(CSV_URL)
                    sdt_target = clean_phone(sdt_nhap)
                    
                    match_found = False
                    for _, row in df.iterrows():
                        # Kiểm tra từng ô trong hàng để tìm số điện thoại
                        for cell in row:
                            if sdt_target == clean_phone(cell):
                                st.session_state.auth = True
                                # Lưu thông tin người dùng (Lấy cột đầu tiên làm tên)
                                st.session_state.user_info = {
                                    "name": str(row.iloc[0]),
                                    "phone": str(sdt_nhap)
                                }
                                match_found = True
                                break
                        if match_found: break
                    
                    if match_found:
                        st.rerun()
                    else:
                        st.error(f"Không tìm thấy SĐT {sdt_nhap} trong danh sách!")
                except:
                    st.error("Lỗi kết nối! Đồng chí hãy kiểm tra quyền 'Chia sẻ' của file Sheets.")

else:
    # --- GIAO DIỆN SAU ĐĂNG NHẬP ---
    user = st.session_state.user_info
    is_admin = clean_phone(user['phone']) == clean_phone(ADMIN_PHONE)
    
    st.sidebar.title(f"Chào Đ/c \n{user['name']}")
    
    menu = ["🏠 Điểm danh", "📖 Tài liệu"]
    if is_admin: menu.append("📊 QUẢN TRỊ")
    
    choice = st.sidebar.radio("CHỨC NĂNG", menu)

    if choice == "🏠 Điểm danh":
        st.header("Điểm danh họp Chi bộ")
        if st.button("XÁC NHẬN CÓ MẶT", use_container_width=True):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['phone'], user['name'], "Có mặt"]):
                st.success("Đã điểm danh thành công!")
                st.balloons()

    elif choice == "📊 QUẢN TRỊ":
        st.title("PHÒNG QUẢN TRỊ")
        st.write("Dữ liệu điểm danh mới nhất:")
        try:
            # Đọc lại file để cập nhật dữ liệu mới
            df_log = pd.read_csv(CSV_URL) 
            st.dataframe(df_log.tail(10), use_container_width=True)
        except:
            st.info("Chưa có dữ liệu.")

    if st.sidebar.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()
