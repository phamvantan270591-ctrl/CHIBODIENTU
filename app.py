import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

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
    st.session_state.user_data = None

if not st.session_state.auth:
    st.title("🏛️ CHI BỘ ĐIỆN TỬ")
    st.subheader("Xác thực Đảng viên")
    with st.form("login_form"):
        sdt_nhap = st.text_input("Nhập số điện thoại của đồng chí:").strip()
        if st.form_submit_button("VÀO HỆ THỐNG"):
            try:
                df = pd.read_csv(CSV_URL)
                df.columns = [c.strip() for c in df.columns]
                sdt_target = clean_num(sdt_nhap)
                
                match_row = None
                for _, row in df.iterrows():
                    for cell in row:
                        if sdt_target != "" and sdt_target in clean_num(cell):
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    st.session_state.auth = True
                    # Tìm tên chính xác để hiển thị
                    display_name = "Đồng chí"
                    for k, v in match_row.items():
                        if "Họ tên" in k or "Ho ten" in k:
                            display_name = str(v)
                            break
                    if display_name == "Đồng chí":
                        for v in match_row.values():
                            if not str(v).isdigit() and len(str(v)) > 3:
                                display_name = str(v)
                                break
                    
                    # Lưu toàn bộ dữ liệu vào session
                    match_row['Display_Name'] = display_name
                    match_row['Login_Phone'] = sdt_nhap
                    st.session_state.user_data = match_row
                    st.rerun()
                else:
                    st.error(f"Không tìm thấy số {sdt_nhap} trong danh sách!")
            except:
                st.error("Lỗi kết nối dữ liệu! Hãy kiểm tra quyền chia sẻ file Sheets.")
else:
    user = st.session_state.user_data
    is_admin = clean_num(user['Login_Phone']) == clean_num(ADMIN_PHONE)
    
    st.sidebar.markdown(f"### Chào đồng chí:\n**{user['Display_Name']}**")
    menu = ["🏠 Điểm danh họp", "📖 Tài liệu sinh hoạt", "👤 Hồ sơ cá nhân"]
    if is_admin:
        menu.append("📊 QUẢN TRỊ CHI BỘ")
    
    choice = st.sidebar.radio("CHỨC NĂNG", menu)

    # 1. ĐIỂM DANH
    if choice == "🏠 Điểm danh họp":
        st.header("📝 Điểm danh họp Chi bộ")
        if st.button("XÁC NHẬN CÓ MẶT", use_container_width=True):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['Login_Phone'], user['Display_Name'], "Có mặt"]):
                st.success(f"Đã ghi nhận điểm danh cho đồng chí {user['Display_Name']}")
                st.balloons()

    # 2. TÀI LIỆU
    elif choice == "📖 Tài liệu sinh hoạt":
        st.header("📖 Tài liệu & Nghị quyết")
        st.info("Nội dung học tập tháng 04/2026")
        st.write("- Chuyên đề: Chuyển đổi số trong công tác Đảng.")
        st.write("- Tài liệu sinh hoạt chi bộ định kỳ.")

    # 3. HỒ SƠ CÁ NHÂN (PHẦN ĐỒNG CHÍ ĐANG BỊ LỖI)
    elif choice == "👤 Hồ sơ cá nhân":
        st.header("👤 Thông tin Đảng viên")
        st.write(f"**Họ và tên:** {user['Display_Name']}")
        st.write(f"**Số điện thoại:** {user['Login_Phone']}")
        # Hiển thị thêm các thông tin khác nếu có trong file Sheets
        for k, v in user.items():
            if k not in ['Display_Name', 'Login_Phone', 'phone_clean'] and "Unnamed" not in k:
                st.write(f"**{k}:** {v}")

    # 4. QUẢN TRỊ
    elif is_admin and choice == "📊 QUẢN TRỊ CHI BỘ":
        st.title("🖥️ QUẢN TRỊ")
        try:
            df_all = pd.read_csv(CSV_URL)
            st.write("Toàn bộ danh sách trong Sheets:")
            st.dataframe(df_all, use_container_width=True)
        except:
            st.error("Không thể tải dữ liệu.")

    if st.sidebar.button("Đăng xuất"):
        st.session_state.auth = False
        st.session_state.user_data = None
        st.rerun()
