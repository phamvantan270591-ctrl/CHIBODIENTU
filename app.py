import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CẤU HÌNH HỆ THỐNG ---
# Link Google Sheets của đồng chí (để đọc dữ liệu)
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

# Link Apps Script (để ghi dữ liệu) - Đã tích hợp link đồng chí gửi
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

st.set_page_config(page_title="Chi bộ Điện tử", page_icon="🏛️")

# --- HÀM GỬI DỮ LIỆU VỀ GOOGLE SHEETS ---
def send_to_sheets(sheet_name, row_data):
    payload = {
        "sheetName": sheet_name,
        "values": row_data
    }
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload))
        return True
    except:
        return False

# --- GIAO DIỆN ĐĂNG NHẬP ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #cc0000;'> CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_code=True)
    st.subheader("🔑 Xác thực Đảng viên")
    sdt_nhap = st.text_input("Nhập số điện thoại của đồng chí:", placeholder="Ví dụ: 0912345678")
    
    if st.button("VÀO HỆ THỐNG", use_container_width=True):
        try:
            # Đọc danh sách đảng viên từ Sheets
            df_user = pd.read_csv(CSV_URL + "DanhSach")
            user_row = df_user[df_user['Số điện thoại'].astype(str).str.contains(sdt_nhap)]
            
            if not user_row.empty:
                st.session_state['authenticated'] = True
                st.session_state['user_info'] = user_row.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Số điện thoại không có trong danh sách Chi bộ!")
        except:
            st.error("Lỗi kết nối dữ liệu. Vui lòng kiểm tra file Sheets!")

else:
    user = st.session_state['user_info']
    st.sidebar.title(f"Chào Đ/c \n{user['Họ tên']}")
    menu = st.sidebar.radio("CHỨC NĂNG", ["🏠 Điểm danh họp", "📖 Học tập chuyên đề", "👤 Hồ sơ & Văn bản"])

    # 1. ĐIỂM DANH HỌP
    if menu == "🏠 Điểm danh họp":
        st.header("📝 Điểm danh họp Chi bộ")
        st.info("Họp thường kỳ tháng này diễn ra vào 14h00 ngày 05/05.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ CÓ MẶT", use_container_width=True):
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                data = [now, str(user['Số điện thoại']), user['Họ tên'], "Có mặt", ""]
                if send_to_sheets("NhatKyHop", data):
                    st.success("Đã điểm danh thành công!")
                    st.balloons()
        with col2:
            if st.button("❌ BÁO VẮNG", use_container_width=True):
                st.session_state['absent'] = True
        
        if st.session_state.get('absent'):
            ly_do = st.selectbox("Lý do vắng:", ["Bận việc gia đình", "Đi khám bệnh", "Công tác xa"])
            if st.button("Gửi báo vắng"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                data = [now, str(user['Số điện thoại']), user['Họ tên'], "Vắng", ly_do]
                send_to_sheets("NhatKyHop", data)
                st.warning("Đã gửi báo vắng.")

    # 2. HỌC TẬP CHUYÊN ĐỀ
    elif menu == "📖 Học tập chuyên đề":
        st.header("📖 Điểm danh Học tập")
        chuyen_de = st.selectbox("Chọn chuyên đề học tập:", ["Chuyên đề tư tưởng Hồ Chí Minh", "Nghị quyết Trung ương khóa XIII"])
        if st.button("Xác nhận tham gia học", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data = [now, str(user['Số điện thoại']), user['Họ tên'], chuyen_de]
            if send_to_sheets("NhatKyHocTap", data):
                st.success(f"Đã ghi nhận Đ/c học tập chuyên đề: {chuyen_de}")

    # 3. HỒ SƠ & VĂN BẢN
    elif menu == "👤 Hồ sơ & Văn bản":
        st.header("👤 Hồ sơ cá nhân")
        st.write(f"**Họ tên:** {user['Họ tên']}")
        st.write(f"**Chức vụ:** {user['Chức vụ']}")
        st.write(f"**Ngày vào Đảng:** {user['Ngày vào Đảng']}")
        st.divider()
        st.header("📂 Văn bản nội bộ")
        st.markdown("- [Hướng dẫn sinh hoạt chi bộ số 12](https://google.com)")

    if st.sidebar.button("Đăng xuất"):
        st.session_state['authenticated'] = False
        st.rerun()
