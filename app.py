import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại Admin (Đã thay số của đồng chí)
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BO DIEN TU", layout="centered")

# Hàm làm sạch số điện thoại (Chỉ giữ lại các chữ số)
def clean_phone_number(phone):
    return ''.join(filter(str.isdigit, str(phone)))

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except: return False

# --- KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.title("🏛️ CHI BO DIEN TU")
    st.subheader("Xac thuc Dang vien")
    
    with st.form("login_form"):
        sdt_input = st.text_input("Nhap so dien thoai cua dong chi:").strip()
        submit = st.form_submit_button("VAO HE THONG")
        
        if submit:
            if not sdt_input:
                st.warning("Vui long nhap so dien thoai!")
            else:
                try:
                    # Tải danh sách đảng viên
                    df = pd.read_csv(CSV_URL + "DanhSach")
                    
                    # Làm sạch SĐT người nhập và SĐT trong danh sách để so khớp
                    input_cleaned = clean_phone_number(sdt_input)
                    
                    # Tìm kiếm (so khớp 9 số cuối để tránh lỗi mất số 0 đầu)
                    match = None
                    for index, row in df.iterrows():
                        sheet_phone = clean_phone_number(row['Số điện thoại'])
                        if input_cleaned.endswith(sheet_phone[-9:]) if len(sheet_phone) >= 9 else input_cleaned == sheet_phone:
                            match = row.to_dict()
                            break
                    
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = match
                        st.rerun()
                    else:
                        st.error(f"Khong tim thay SĐT {sdt_input} trong danh sach Chi bo!")
                except Exception as e:
                    st.error(f"Loi ket noi: Vui long kiem tra ten trang tinh 'DanhSach' trong file Sheets!")

else:
    user = st.session_state.user
    # Kiểm tra quyền Quản trị
    user_sdt_clean = clean_phone_number(user['Số điện thoại'])
    admin_sdt_clean = clean_phone_number(ADMIN_PHONE)
    is_admin = user_sdt_clean.endswith(admin_sdt_clean[-9:])

    st.sidebar.title(f"Đ/c: {user['Họ tên']}")
    
    # Menu phân quyền
    nav = ["🏠 Diem danh hop", "📖 Hoc tap", "👤 Ho so"]
    if is_admin:
        nav.append("📊 QUAN LY")
    
    choice = st.sidebar.radio("CHUC NANG", nav)

    # 1. ĐIỂM DANH
    if choice == "🏠 Diem danh hop":
        st.header("Diem danh hop Chi bo")
        if st.button("XAC NHAN CO MAT", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = [now, user['Số điện thoại'], user['Họ tên'], "Có mặt", ""]
            if send_to_sheets("NhatKyHop", data):
                st.success("Da ghi nhan thanh cong!")
                st.balloons()

    # 2. QUẢN LÝ (Chỉ Admin thấy)
    elif choice == "📊 QUAN LY":
        st.title("PHONG DIEU HANH")
        st.subheader("Lich su diem danh moi nhat")
        try:
            df_log = pd.read_csv(CSV_URL + "NhatKyHop")
            st.dataframe(df_log.tail(20), use_container_width=True)
        except:
            st.info("Chua co du lieu diem danh.")

    # 3. CÁC MỤC KHÁC
    elif choice == "📖 Hoc tap":
        st.header("Tai lieu sinh hoat")
        st.write("- Chuyen de thang nay: Hoc tap va lam theo tu tuong HCM")
        
    elif choice == "👤 Ho so":
        st.header("Thong tin ca nhan")
        st.write(f"**Ho ten:** {user['Họ tên']}")
        st.write(f"**Chuc vu:** {user['Chức vụ']}")

    if st.sidebar.button("Dang xuat"):
        st.session_state.auth = False
        st.rerun()
