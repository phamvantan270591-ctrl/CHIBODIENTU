import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link lấy dữ liệu trang đầu (Danh sách Đảng viên)
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Link lấy dữ liệu trang Nhật ký họp
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
# Link Google Script để gửi dữ liệu
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# SỐ ĐIỆN THOẠI QUẢN TRỊ (ADMIN)
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 8px solid #d32f2f; background-color: #f1f1f1; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Giữ lại 9 số cuối để so khớp chính xác 100%"""
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s[-9:] if len(s) >= 9 else s

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
        return True
    except: return False

# --- XỬ LÝ ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Hệ thống quản lý Đảng viên trực tuyến</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại của đồng chí:").strip()
        submit = st.form_submit_button("ĐĂNG NHẬP")
        
        if submit:
            if not sdt_nhap:
                st.warning("Vui lòng nhập số điện thoại!")
            else:
                try:
                    # Đọc dữ liệu từ Sheets
                    df = pd.read_csv(CSV_URL)
                    target = clean_num(sdt_nhap)
                    
                    match_row = None
                    for _, row in df.iterrows():
                        # Kiểm tra từng ô trong hàng để tìm SĐT
                        for cell in row:
                            if target != "" and target == clean_num(cell):
                                match_row = row.to_dict()
                                break
                        if match_row: break
                    
                    if match_row:
                        # Xác định họ tên hiển thị
                        ten = "Đồng chí"
                        for k, v in match_row.items():
                            if any(x in k.lower() for x in ['họ tên', 'tên', 'hoten']):
                                ten = str(v)
                                break
                        
                        st.session_state.auth = True
                        st.session_state.user = {"name": ten, "phone": sdt_nhap, "data": match_row}
                        st.rerun()
                    else:
                        st.error(f"Không tìm thấy SĐT {sdt_nhap} trong danh sách Chi bộ!")
                except Exception as e:
                    st.error("Lỗi kết nối! Đồng chí hãy kiểm tra lại quyền 'Chia sẻ' của file Sheets.")

else:
    u = st.session_state.user
    # KIỂM TRA QUYỀN ADMIN (So sánh 9 số cuối)
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {u['name']}</h3>", unsafe_allow_html=True)
        menu = ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"]
        if is_admin:
            menu.append("📊 QUẢN TRỊ")
        
        choice = st.radio("CHỨC NĂNG", menu)
        st.write("---")
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    # --- NỘI DUNG TƯƠNG ỨNG ---
    if choice == "🏠 Điểm danh":
        st.subheader("📝 Xác nhận dự họp")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [gio, u['phone'], u['name'], "Có mặt"]):
                st.success("Đã điểm danh thành công!")
                st.balloons()

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin cá nhân")
        st.markdown(f"""
        <div class="profile-card">
            <p><b>Họ và tên:</b> {u['name']}</p>
            <p><b>Số điện thoại:</b> {u['phone']}</p>
            <p><b>Quyền hạn:</b> {"Quản trị viên" if is_admin else "Đảng viên"}</p>
        </div>
        """, unsafe_allow_html=True)

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ PHÒNG ĐIỀU HÀNH</h2>", unsafe_allow_html=True)
        try:
            df_ds = pd.read_csv(CSV_URL)
            df_log = pd.read_csv(LOG_URL)
            
            # Thống kê
            tong = len(df_ds)
            da_den = df_log[df_log.iloc[:, 3] == "Có mặt"].iloc[:, 1].astype(str).apply(clean_num).nunique()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng số", tong)
            c2.metric("Có mặt", da_den)
            c3.metric("Vắng", tong - da_den)
            
            st.write("---")
            st.subheader("📋 Nhật ký điểm danh (Mới nhất)")
            st.dataframe(df_log.tail(10), use_container_width=True)
        except:
            st.info("Đang chờ dữ liệu điểm danh thực tế...")
