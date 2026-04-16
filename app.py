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
                # Chuẩn hóa tên cột để tránh lỗi tiếng Việt có dấu
                df.columns = [c.strip() for c in df.columns]
                
                sdt_target = clean_num(sdt_nhap)
                match_row = None
                
                for _, row in df.iterrows():
                    for cell in row:
                        if sdt_target != "" and sdt_target in clean_num(cell):
                            match_row = row
                            break
                    if match_row is not None: break
                
                if match_row is not None:
                    st.session_state.auth = True
                    # TÌM HỌ TÊN: Ưu tiên cột có chữ 'Họ tên', nếu không lấy cột đầu tiên không phải số
                    ho_ten = "Đồng chí"
                    for col in df.columns:
                        if "Họ tên" in col or "Ho ten" in col:
                            ho_ten = str(match_row[col])
                            break
                    if ho_ten == "Đồng chí":
                        for val in match_row:
                            if not str(val).isdigit() and len(str(val)) > 3:
                                ho_ten = str(val)
                                break
                                
                    st.session_state.user = {"name": ho_ten, "phone": sdt_nhap}
                    st.rerun()
                else:
                    st.error(f"Không tìm thấy số {sdt_nhap} trong danh sách!")
            except:
                st.error("Lỗi kết nối dữ liệu!")
else:
    user = st.session_state.user
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    st.sidebar.markdown(f"### Chào đồng chí:\n**{user['name']}**")
    menu = ["🏠 Điểm danh họp", "📖 Tài liệu sinh hoạt", "👤 Hồ sơ cá nhân"]
    if is_admin:
        menu.append("📊 QUẢN TRỊ CHI BỘ")
    
    choice = st.sidebar.radio("CHỨC NĂNG", menu)

    if choice == "🏠 Điểm danh họp":
        st.header("📝 Điểm danh họp Chi bộ")
        if st.button("XÁC NHẬN CÓ MẶT", use_container_width=True):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['phone'], user['name'], "Có mặt"]):
                st.success(f"Đồng chí {user['name']} đã điểm danh thành công!")
                st.balloons()

    elif is_admin and choice == "📊 QUẢN TRỊ CHI BỘ":
        st.title("🖥️ QUẢN TRỊ CHI BỘ")
        try:
            df_view = pd.read_csv(CSV_URL)
            st.write("Danh sách Đảng viên hiện tại:")
            st.dataframe(df_view, use_container_width=True)
        except:
            st.warning("Không thể tải danh sách.")

    if st.sidebar.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()
