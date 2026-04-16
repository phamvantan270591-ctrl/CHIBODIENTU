import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- PHONG CÁCH GIAO DIỆN ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #d32f2f; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #b71c1c; color: white; }
    [data-testid="stSidebar"] { background-color: #fff5f5; border-right: 2px solid #d32f2f; }
    .profile-card {
        padding: 20px; border-radius: 15px; border-left: 5px solid #d32f2f;
        background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    return ''.join(filter(str.isdigit, str(p)))

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
        return True
    except: return False

# --- HỆ THỐNG ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_data = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Vui lòng xác thực số điện thoại Đảng viên</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        sdt_nhap = st.text_input("📱 Số điện thoại:", placeholder="0927...")
        if st.form_submit_button("ĐĂNG NHẬP"):
            try:
                df = pd.read_csv(CSV_URL)
                sdt_target = clean_num(sdt_nhap)
                match_row = None
                for _, row in df.iterrows():
                    for cell in row:
                        if sdt_target != "" and sdt_target in clean_num(cell):
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    # Tìm tên chuẩn
                    ten = "Đồng chí"
                    for k, v in match_row.items():
                        if any(x in k.lower() for x in ['họ tên', 'hoten', 'tên']):
                            ten = str(v)
                            break
                    st.session_state.auth = True
                    st.session_state.user_data = {"name": ten, "phone": sdt_nhap, "full": match_row}
                    st.rerun()
                else: st.error("Không tìm thấy số điện thoại này!")
            except: st.error("Lỗi kết nối dữ liệu Sheets!")
else:
    user = st.session_state.user_data
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {user['name']}</h3>", unsafe_allow_html=True)
        menu = st.radio("CHỨC NĂNG", ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"])
        if is_admin: st.write("---"); menu = st.radio("QUẢN TRỊ", [menu, "📊 Báo cáo"])
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if menu == "🏠 Điểm danh":
        st.subheader("📝 Điểm danh họp Chi bộ")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['phone'], user['name'], "Có mặt"]):
                st.success("Đã điểm danh thành công!")
                st.balloons()

    elif menu == "📖 Tài liệu":
        st.subheader("📖 Tài liệu sinh hoạt")
        st.info("Nội dung học tập tháng 04/2026")
        st.write("1. Nghị quyết về công tác cán bộ.")
        st.write("2. Chuyên đề Chuyển đổi số trong Đảng.")

    elif menu == "👤 Hồ sơ":
        st.subheader("👤 Hồ sơ Đảng viên")
        st.markdown(f"""
        <div class="profile-card">
            <p><b>Họ và tên:</b> {user['name']}</p>
            <p><b>Số điện thoại:</b> {user['phone']}</p>
            <p><b>Trạng thái:</b> <span style='color: green;'>Đang sinh hoạt</span></p>
        </div>
        """, unsafe_allow_html=True)

    elif menu == "📊 Báo cáo" and is_admin:
        st.subheader("📊 Quản lý danh sách")
        try:
            df_all = pd.read_csv(CSV_URL)
            st.dataframe(df_all, use_container_width=True)
        except: st.error("Không tải được dữ liệu.")
