import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CẤU HÌNH HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# SỐ ĐIỆN THOẠI QUẢN TRỊ VIÊN (Của đồng chí)
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BO DIEN TU", layout="centered")

# Hàm gửi dữ liệu về Sheets
def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except:
        return False

# --- CƠ CHẾ ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.title("🏛️ CHI BO DIEN TU")
    st.subheader("Xac thuc Dang vien")
    
    # Dùng form để xử lý đăng nhập 1 lần ăn ngay
    with st.form("login_section"):
        sdt_input = st.text_input("Nhap so dien thoai cua dong chi:", placeholder="Vi du: 09...")
        btn_login = st.form_submit_button("VAO HE THONG")
        
        if btn_login:
            if not sdt_input:
                st.warning("Vui long nhap so dien thoai!")
            else:
                try:
                    # Đọc danh sách từ Sheets
                    df = pd.read_csv(CSV_URL + "DanhSach")
                    df['Số điện thoại'] = df['Số điện thoại'].astype(str).str.strip()
                    
                    # Kiểm tra số điện thoại
                    user_match = df[df['Số điện thoại'] == sdt_input.strip()]
                    
                    if not user_match.empty:
                        st.session_state.auth = True
                        st.session_state.user = user_match.iloc[0].to_dict()
                        st.rerun() # Tự động chuyển trang ngay lập tức
                    else:
                        st.error("So dien thoai khong co trong danh sach!")
                except Exception as e:
                    st.error("Loi ket noi du lieu. Vui long kiem tra file Sheets!")

else:
    user = st.session_state.user
    # Kiểm tra xem có phải là đồng chí (Admin) không
    is_admin = str(user['Số điện thoại']) == ADMIN_PHONE

    # --- MENU ĐIỀU HƯỚNG ---
    st.sidebar.title(f"Chào Đ/c \n{user['Họ tên']}")
    
    options = ["🏠 Diem danh hop", "📖 Hoc tap", "👤 Ho so ca nhan"]
    if is_admin:
        options.append("📊 QUAN LY CHI BO") # Chỉ Admin mới thấy mục này
        
    choice = st.sidebar.radio("CHUC NANG", options)

    # 1. PHẦN ĐIỂM DANH (Dành cho tất cả mọi người)
    if choice == "🏠 Diem danh hop":
        st.header("📝 Diem danh hop Chi bo")
        st.info("Bam nut duoi day de xac nhan su co mat cua dong chi.")
        
        if st.button("XAC NHAN CO MAT", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = [now, user['Số điện thoại'], user['Họ tên'], "Có mặt", ""]
            if send_to_sheets("NhatKyHop", data):
                st.success("Da ghi nhan thanh cong!")
                st.balloons()

    # 2. PHẦN QUẢN LÝ (CHỈ ĐỒNG CHÍ MỚI THẤY)
    elif is_admin and choice == "📊 QUAN LY CHI BO":
        st.title("🖥️ PHONG DIEU HANH QUAN TRI")
        
        tab1, tab2 = st.tabs(["Lich su Diem danh", "Danh sach Chi bo"])
        
        with tab1:
            st.subheader("Danh sach vua diem danh (Moi nhat)")
            try:
                df_logs = pd.read_csv(CSV_URL + "NhatKyHop")
                st.dataframe(df_logs.tail(15), use_container_width=True)
            except:
                st.info("Chua co du lieu diem danh moi.")
                
        with tab2:
            st.subheader("Danh sach Dang vien hien tai")
            try:
                df_ds = pd.read_csv(CSV_URL + "DanhSach")
                st.write(f"Tong so: {len(df_ds)} dong chi.")
                st.table(df_ds[['Họ tên', 'Chức vụ', 'Số điện thoại']])
            except:
                st.error("Khong the tai danh sach.")

    # 3. CÁC MỤC KHÁC
    elif choice == "📖 Hoc tap":
        st.header("Tai lieu Hoc tap")
        st.write("- Chuyen de thang nay: Tu tuong Ho Chi Minh.")
        
    elif choice == "👤 Ho so ca nhan":
        st.header("Thong tin Dang vien")
        st.write(f"**Ho ten:** {user['Họ tên']}")
        st.write(f"**Chuc vu:** {user['Chức vụ']}")
        st.write(f"**So dien thoai:** {user['Số điện thoại']}")

    # Nút đăng xuất
    if st.sidebar.button("Dang xuat"):
        st.session_state.auth = False
        st.rerun()
