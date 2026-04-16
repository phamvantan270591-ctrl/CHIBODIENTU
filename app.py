import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- GIAO DIỆN CSS (ĐÃ TINH CHỈNH ĐẸP HƠN) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 4em;
        background-color: #d32f2f; color: white; font-weight: bold; font-size: 20px;
        border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #b71c1c; color: white; transform: scale(1.01); }
    .profile-card {
        padding: 25px; border-radius: 15px; border-left: 10px solid #d32f2f;
        background-color: #f9f9f9; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 18px;
    }
    .st-expander { border: none !important; box-shadow: none !important; }
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

# --- ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user_data = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f; margin-bottom: 0;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Hệ thống quản lý sinh hoạt Đảng</p>", unsafe_allow_html=True)
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="Nhập tại đây...")
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
                    ten = "Đồng chí"
                    for k, v in match_row.items():
                        if any(x in k.lower() for x in ['họ tên', 'hoten', 'tên']):
                            ten = str(v)
                            break
                    st.session_state.auth = True
                    st.session_state.user_data = {"name": ten, "phone": sdt_nhap}
                    st.rerun()
                else: st.error("Không tìm thấy thông tin đồng chí trong danh sách!")
            except: st.error("Lỗi kết nối dữ liệu. Vui lòng kiểm tra file Sheets.")
else:
    user = st.session_state.user_data
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {user['name']}</h3>", unsafe_allow_html=True)
        menu = st.radio("CHỨC NĂNG", ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"])
        if is_admin: 
            st.write("---")
            menu = st.radio("QUẢN TRỊ", [menu, "📊 Báo cáo"])
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if menu == "🏠 Điểm danh":
        st.subheader("📝 Xác nhận dự họp")
        st.write("Mời đồng chí xác nhận tham dự buổi sinh hoạt Chi bộ hôm nay.")
        
        # Ẩn hàng giờ Việt Nam, chỉ lấy ngầm bên dưới
        tz_vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
        gio_gui = datetime.now(tz_vietnam).strftime("%H:%M:%S %d/%m/%Y")
        
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            if send_to_sheets("NhatKyHop", [gio_gui, user['phone'], user['name'], "Có mặt"]):
                st.success(f"Đã điểm danh thành công lúc {gio_gui}")
                st.balloons()

    elif menu == "📖 Tài liệu":
        st.subheader("📖 Tài liệu sinh hoạt")
        with st.expander("📌 Nội dung tháng 04/2026", expanded=True):
            st.write("- Triển khai ứng dụng công nghệ trong quản lý Đảng viên.")
            st.write("- Học tập chuyên đề tư tưởng Hồ Chí Minh.")

    elif menu == "👤 Hồ sơ":
        st.subheader("👤 Thông tin cá nhân")
        st.markdown(f"""
        <div class="profile-card">
            <p style='margin-bottom:8px;'><b>Họ và tên:</b> {user['name']}</p>
            <p style='margin-bottom:8px;'><b>Số điện thoại:</b> {user['phone']}</p>
            <p style='margin-bottom:0px;'><b>Trạng thái:</b> <span style='color: #2e7d32; font-weight:bold;'>Đang sinh hoạt</span></p>
        </div>
        """, unsafe_allow_html=True)

    elif menu == "📊 Báo cáo" and is_admin:
        st.subheader("📊 Quản trị viên")
        try:
            df_all = pd.read_csv(CSV_URL)
            st.dataframe(df_all, use_container_width=True)
        except: st.error("Không tải được dữ liệu.")
