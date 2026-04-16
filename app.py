import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Thêm tham số tqx=out:csv để ép Google trả về định dạng chuẩn nhất
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

# --- GIAO DIỆN ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
    .profile-card { padding: 20px; border-radius: 12px; border-left: 8px solid #d32f2f; background-color: #f1f1f1; }
    </style>
    """, unsafe_allow_html=True)

def clean_num(p):
    """Xóa sạch mọi ký tự không phải số và lấy 9 số cuối"""
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s[-9:] if len(s) >= 9 else s

def send_to_sheets(sheet_name, row_data):
    payload = {"sheetName": sheet_name, "values": row_data}
    try:
        requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=10)
        return True
    except: return False

# --- ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:").strip()
        if st.form_submit_button("ĐĂNG NHẬP"):
            try:
                # Đọc dữ liệu (ép pandas không đoán định dạng để tránh lỗi số 0 đầu)
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
                    ten = "Đồng chí"
                    for k, v in match_row.items():
                        if any(x in str(k).lower() for x in ['họ tên', 'tên', 'hoten']):
                            ten = str(v)
                            break
                    st.session_state.auth = True
                    st.session_state.user = {"name": ten, "phone": sdt_nhap}
                    st.rerun()
                else:
                    st.error(f"❌ Không tìm thấy SĐT {sdt_nhap}. Đồng chí kiểm tra lại danh sách trong Sheets nhé!")
            except Exception as e:
                st.error("⚠️ Không thể kết nối với Google Sheets. Hãy chắc chắn đồng chí đã mở quyền 'Bất kỳ ai có đường liên kết đều có thể xem'.")

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
                st.success("Đã điểm danh thành công!")
                st.balloons()

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ QUẢN TRỊ</h2>", unsafe_allow_html=True)
        try:
            df_log = pd.read_csv(LOG_URL)
            st.metric("Tổng số người đã điểm danh", len(df_log))
            st.dataframe(df_log.tail(10), use_container_width=True)
        except: st.info("Chưa có nhật ký họp.")
