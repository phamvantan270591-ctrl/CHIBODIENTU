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

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# Tùy chỉnh CSS để giao diện đẹp hơn
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #cc0000;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #ff0000; color: white; }
    .css-10trblm { color: #cc0000; } /* Màu tiêu đề sidebar */
    .st-emotion-cache-6qob1r { background-color: #ffffff; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

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
    st.markdown("<h1 style='text-align: center; color: #cc0000;'>🏛️ CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Hệ thống quản lý sinh hoạt Đảng trực tuyến</p>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("login_form"):
            sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="Ví dụ: 0927...")
            submit = st.form_submit_button("ĐĂNG NHẬP HỆ THỐNG")
            
            if submit:
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
                        display_name = "Đồng chí"
                        for k, v in match_row.items():
                            if "Họ tên" in k or "Ho ten" in k:
                                display_name = str(v)
                                break
                        match_row['Display_Name'] = display_name
                        match_row['Login_Phone'] = sdt_nhap
                        st.session_state.user_data = match_row
                        st.rerun()
                    else:
                        st.error("❌ Không tìm thấy số điện thoại trong danh sách!")
                except:
                    st.error("⚠️ Lỗi kết nối dữ liệu. Vui lòng thử lại sau.")
else:
    user = st.session_state.user_data
    is_admin = clean_num(user['Login_Phone']) == clean_num(ADMIN_PHONE)
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h2 style='color: #cc0000;'>🇻🇳 CHI BỘ</h2>", unsafe_allow_html=True)
        st.write(f"Chào đồng chí:")
        st.subheader(user['Display_Name'])
        st.write("---")
        menu = ["🏠 Điểm danh họp", "📖 Tài liệu học tập", "👤 Hồ sơ cá nhân"]
        if is_admin:
            menu.append("📊 QUẢN TRỊ VIÊN")
        choice = st.radio("MENU CHỨC NĂNG", menu)
        st.write("---")
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    # --- NỘI DUNG CHÍNH ---
    if choice == "🏠 Điểm danh họp":
        st.markdown("<h2 style='color: #cc0000;'>📝 ĐIỂM DANH SINH HOẠT</h2>", unsafe_allow_html=True)
        st.info(f"Hôm nay là ngày {datetime.now().strftime('%d/%m/%Y')}. Mời đồng chí xác nhận sự có mặt.")
        
        if st.button("✅ BẤM VÀO ĐÂY ĐỂ ĐIỂM DANH"):
            time_now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [time_now, user['Login_Phone'], user['Display_Name'], "Có mặt"]):
                st.success("Chúc mừng! Đồng chí đã điểm danh thành công.")
                st.balloons()

    elif choice == "📖 Tài liệu học tập":
        st.markdown("<h2 style='color: #cc0000;'>📖 TÀI LIỆU CHI BỘ</h2>", unsafe_allow_html=True)
        with st.expander("📌 Nghị quyết tháng 04/2026", expanded=True):
            st.write("Nội dung: Đẩy mạnh ứng dụng công nghệ thông tin trong sinh hoạt Chi bộ.")
        with st.expander("📌 Chuyên đề học tập"):
            st.write("Chủ đề: Học tập và làm theo tư tưởng Hồ Chí Minh về tinh thần tự học.")

    elif choice == "👤 Hồ sơ cá nhân":
        st.markdown("<h2 style='color: #cc0000;'>👤 HỒ SƠ ĐẢNG VIÊN</h2>", unsafe_allow_html=True)
        # Hiển thị thông tin dạng bảng cho đẹp
        data = {
            "Trường thông tin": ["Họ và tên", "Số điện thoại liên lạc", "Trạng thái"],
            "Giá trị": [user['Display_Name'], user['Login_Phone'], "Đang sinh hoạt"]
        }
        st.table(pd.DataFrame(data))
        
        # Hiện thêm các cột khác từ file Sheets nếu có
        with st.expander("Xem thêm chi tiết"):
            for k, v in user.items():
                if k not in ['Display_Name', 'Login_Phone', 'phone_clean'] and "Unnamed" not in k:
                    st
