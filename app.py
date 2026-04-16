import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Link này dùng để đọc trang Nhật Ký Họp (giả sử là trang thứ 2, hoặc đồng chí thay bằng link cụ thể)
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_PHONE = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 8px solid #d32f2f; background-color: #f9f9f9; }
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
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:")
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
                else: st.error("Không tìm thấy thông tin!")
            except: st.error("Lỗi kết nối dữ liệu!")
else:
    user = st.session_state.user_data
    is_admin = clean_num(user['phone']) == clean_num(ADMIN_PHONE)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {user['name']}</h3>", unsafe_allow_html=True)
        # Menu sẽ thay đổi nếu là Admin
        options = ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"]
        if is_admin:
            options.append("📊 QUẢN TRỊ CHI BỘ")
        
        choice = st.radio("CHỨC NĂNG", options)
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    # --- NỘI DUNG ---
    if choice == "🏠 Điểm danh":
        st.subheader("📝 Điểm danh họp Chi bộ")
        tz_vietnam = pytz.timezone('Asia/Ho_Chi_Minh')
        gio_gui = datetime.now(tz_vietnam).strftime("%H:%M:%S %d/%m/%Y")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            if send_to_sheets("NhatKyHop", [gio_gui, user['phone'], user['name'], "Có mặt"]):
                st.success(f"Đã điểm danh thành công!")
                st.balloons()

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin cá nhân")
        st.markdown(f"<div class='profile-card'><b>Họ và tên:</b> {user['name']}<br><b>SĐT:</b> {user['phone']}<br><b>Trạng thái:</b> Đang sinh hoạt</div>", unsafe_allow_html=True)

    # --- GIAO DIỆN QUẢN TRỊ (CHỈ DÀNH RIÊNG CHO ĐỒNG CHÍ) ---
    elif choice == "📊 QUẢN TRỊ CHI BỘ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ PHÒNG ĐIỀU HÀNH QUẢN TRỊ</h2>", unsafe_allow_html=True)
        
        try:
            # Tải dữ liệu từ 2 bảng
            df_ds = pd.read_csv(CSV_URL)
            df_log = pd.read_csv(LOG_URL)
            
            # Tính toán thông số
            tong_so = len(df_ds)
            da_diem_danh = df_log[df_log.iloc[:, 3] == "Có mặt"].iloc[:, 1].nunique() # Đếm số SĐT không trùng nhau
            vangs = tong_so - da_diem_danh
            
            # Hiển thị thẻ thống kê
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng số Đảng viên", f"{tong_so}")
            col2.metric("Đã có mặt", f"{da_diem_danh}", delta=f"{da_diem_danh/tong_so*100:.0f}%", delta_color="normal")
            col3.metric("Còn vắng", f"{vangs}", delta_color="inverse")
            
            st.write("---")
            st.subheader("📋 Danh sách Đảng viên đã điểm danh")
            # Hiển thị bảng nhật ký mới nhất
            st.dataframe(df_log.tail(20), use_container_width=True)
            
        except Exception as e:
            st.warning("Đang chờ dữ liệu điểm danh đầu tiên...")
            st.info("Lưu ý: Đồng chí cần đảm bảo trang 'NhatKyHop' trong file Sheets đã có ít nhất 1 dòng dữ liệu.")
