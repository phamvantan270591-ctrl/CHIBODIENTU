import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link truy xuất dữ liệu dạng CSV sạch
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại Admin (Đồng chí)
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- CSS GIAO DIỆN SANG TRỌNG ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; font-size: 18px; border: none; }
    .stMetric { background-color: #fff5f5; padding: 15px; border-radius: 10px; border: 1px solid #ffcccc; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 10px solid #d32f2f; background-color: #f8f9fa; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Chuẩn hóa số điện thoại: bỏ số 0 đầu, lấy các số còn lại"""
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
        return True
    except: return False

# --- KHỞI TẠO PHIÊN LÀM VIỆC ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    with st.container():
        with st.form("login"):
            sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                try:
                    # Đọc danh sách từ Sheets
                    df = pd.read_csv(CSV_URL, dtype=str)
                    target = clean_num(sdt_nhap)
                    
                    match_row = None
                    for _, row in df.iterrows():
                        for val in row.values:
                            if target != "" and target == clean_num(val):
                                match_row = row.to_dict()
                                break
                        if match_row: break
                    
                    if match_row:
                        # Tìm tên hiển thị
                        ten = "Đồng chí"
                        for k, v in match_row.items():
                            if any(x in str(k).lower() for x in ['họ tên', 'tên', 'hoten']):
                                ten = str(v)
                                break
                        st.session_state.auth = True
                        st.session_state.user = {"name": ten, "phone": sdt_nhap}
                        st.rerun()
                    else:
                        st.error(f"❌ Số {sdt_nhap} chưa có trong danh sách Chi bộ. Đồng chí hãy thêm số này vào file Sheets trước.")
                except:
                    st.error("⚠️ Lỗi kết nối dữ liệu. Đồng chí hãy kiểm tra quyền chia sẻ file Sheets.")
else:
    u = st.session_state.user
    is_admin = clean_num(u['phone']) == clean_num(ADMIN_NUM)
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #d32f2f;'>Đ/c {u['name']}</h3>", unsafe_allow_html=True)
        menu = ["🏠 Điểm danh", "📖 Tài liệu", "👤 Hồ sơ"]
        if is_admin: menu.append("📊 QUẢN TRỊ")
        choice = st.radio("CHỨC NĂNG", menu)
        if st.button("Đăng xuất"):
            st.session_state.auth = False
            st.rerun()

    if choice == "🏠 Điểm danh":
        st.subheader("📝 Xác nhận dự họp")
        if st.button("✅ XÁC NHẬN CÓ MẶT"):
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            if send_to_sheets("NhatKyHop", [gio, u['phone'], u['name'], "Có mặt"]):
                st.success(f"Đã ghi nhận điểm danh thành công!")
                st.balloons()

    elif choice == "👤 Hồ sơ":
        st.subheader("👤 Thông tin cá nhân")
        st.markdown(f"""
        <div class="profile-card">
            <p><b>Họ và tên:</b> {u['name']}</p>
            <p><b>SĐT:</b> {u['phone']}</p>
            <p><b>Chức vụ:</b> {'Quản trị viên' if is_admin else 'Đảng viên'}</p>
        </div>
        """, unsafe_allow_html=True)

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ BẢNG ĐIỀU HÀNH</h2>", unsafe_allow_html=True)
        try:
            df_ds = pd.read_csv(CSV_URL)
            df_log = pd.read_csv(LOG_URL)
            t_tong = len(df_ds)
            t_den = df_log[df_log.iloc[:, 3] == "Có mặt"].iloc[:, 1].astype(str).apply(clean_num).nunique()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng số", t_tong)
            c2.metric("Có mặt", t_den)
            c3.metric("Vắng", t_tong - t_den)
            
            st.write("---")
            st.subheader("📋 Nhật ký điểm danh gần đây")
            st.dataframe(df_log.tail(10), use_container_width=True)
        except:
            st.info("Đang chờ dữ liệu điểm danh thực tế từ trang 'NhatKyHop'...")
