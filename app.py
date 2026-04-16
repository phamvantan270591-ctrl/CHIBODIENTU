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
    
    choice = st.sidebar.radio("CHỨC NĂNG", menu)

    # 1. MỤC ĐIỂM DANH
    if choice == "🏠 Điểm danh họp":
        st.header("📝 Điểm danh họp Chi bộ")
        st.write("Đồng chí vui lòng xác nhận sự có mặt trong buổi sinh hoạt.")
        if st.button("XÁC NHẬN CÓ MẶT", use_container_width=True):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['phone'], user['name'], "Có mặt"]):
                st.success("Đã ghi nhận điểm danh thành công!")
                st.balloons()

    # 2. MỤC TÀI LIỆU
    elif choice == "📖 Tài liệu sinh hoạt":
        st.header("📖 Tài liệu học tập & Nghị quyết")
        st.info("Nội dung này được cập nhật từ Chi ủy.")
        st.markdown("""
        * **Nghị quyết tháng 04/2026:** Tập trung công tác chuyển đổi số.
        * **Chuyên đề:** Học tập và làm theo tư tưởng, đạo đức, phong cách Hồ Chí Minh.
        * *Lưu ý: Đồng chí có thể xem chi tiết tài liệu tại nhóm Zalo Chi bộ.*
        """)

    # 3. MỤC HỒ SƠ
    elif choice == "👤 Hồ sơ cá nhân":
        st.header("👤 Thông tin Đảng viên")
        st.write(f"- **Họ và tên:** {user['name']}")
        st.write(f"- **Số điện thoại:** {user['phone']}")
        st.write("- **Trạng thái:** Đang sinh hoạt")

    # 4. MỤC QUẢN TRỊ (CHỈ ĐỒNG CHÍ THẤY)
    elif is_admin and choice == "📊 QUẢN TRỊ CHI BỘ":
        st.title("🖥️ PHÒNG ĐIỀU HÀNH QUẢN TRỊ")
        st.subheader("Danh sách vừa điểm danh (Mới nhất)")
        try:
            # Đọc lại toàn bộ file Sheets để hiện danh sách Đảng viên
            df_view = pd.read_csv(CSV_URL)
            st.write("Danh sách Đảng viên trong Chi bộ:")
            st.dataframe(df_view, use_container_width=True)
            st.write("---")
            st.write("*Gợi ý: Đồng chí mở file Google Sheets trang 'NhatKyHop' để xem chi tiết giờ điểm danh.*")
        except:
            st.warning("Không thể tải danh sách quản trị.")

    # Nút Đăng xuất
    if st.sidebar.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()
