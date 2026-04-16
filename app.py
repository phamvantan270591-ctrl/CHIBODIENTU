import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link này sẽ lấy dữ liệu trang đầu tiên bất kể tên là gì
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại của đồng chí quản trị
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BO DIEN TU", layout="centered")

# Hàm làm sạch SĐT: Xóa sạch dấu chấm, dấu cách, chỉ giữ lại số
def clean_num(p):
    return ''.join(filter(str.isdigit, str(p)))

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except: return False

# --- ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.title("🏛️ CHI BỘ ĐIỆN TỬ")
    with st.form("login_form"):
        sdt_nhap = st.text_input("Nhập số điện thoại:").strip()
        submit = st.form_submit_button("VÀO HỆ THỐNG")
        
        if submit:
            try:
                df = pd.read_csv(CSV_URL)
                sdt_target = clean_num(sdt_nhap)
                
                match = None
                for _, row in df.iterrows():
                    # Quét tất cả các ô trong hàng để tìm SĐT
                    for cell in row:
                        if sdt_target != "" and sdt_target in clean_num(cell):
                            match = row.to_dict()
                            break
                    if match: break
                
                if match:
                    st.session_state.auth = True
                    # Lấy giá trị ô đầu tiên trong hàng làm Tên
                    st.session_state.user = {"name": str(list(match.values())[0]), "phone": sdt_nhap}
                    st.rerun()
                else:
                    st.error(f"Không tìm thấy số {sdt_nhap} trong danh sách!")
            except:
                st.error("Lỗi kết nối! Đồng chí hãy kiểm tra lại quyền Chia sẻ file Sheets.")

else:
    # --- GIAO DIỆN CHÍNH ---
    user = st.session_state.user
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    st.sidebar.title(f"Chào Đ/c \n{user['name']}")
    menu = ["🏠 Điểm danh", "📖 Tài liệu"]
    if is_admin: menu.append("📊 QUẢN TRỊ")
    choice = st.sidebar.radio("CHỨC NĂNG", menu)

    if choice == "🏠 Điểm danh":
        st.header("Điểm danh họp Chi bộ")
        if st.button("XÁC NHẬN CÓ MẶT", use_container_width=True):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            # Gửi vào trang NhatKyHop (Đồng chí nhớ tạo trang này trong Sheets nhé)
            if send_to_sheets("NhatKyHop", [time_now, user['phone'], user['name'], "Có mặt"]):
                st.success("Đã điểm danh thành công!")
                st.balloons()

    elif choice == "📊 QUAN TRI":
        st.title("BẢNG QUẢN TRỊ")
        st.write("Dữ liệu từ Sheets:")
        try:
            df_view = pd.read_csv(CSV_URL)
            st.dataframe(df_view, use_container_width=True)
        except: st.info("Chưa có dữ liệu.")

    if st.sidebar.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()
