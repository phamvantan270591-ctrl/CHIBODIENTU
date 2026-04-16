import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz

# --- THÔNG TIN HỆ THỐNG ---
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

# Số điện thoại Admin chuẩn
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ĐIỆN TỬ", layout="centered")

def clean_num(p):
    """Xóa mọi ký tự lạ, chỉ giữ lại số và bỏ số 0 đầu để so sánh"""
    if pd.isna(p): return ""
    s = ''.join(filter(str.isdigit, str(p)))
    return s.lstrip('0')

# --- ĐĂNG NHẬP ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🇻🇳 CHI BỘ ĐIỆN TỬ</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sdt_nhap = st.text_input("📱 Nhập số điện thoại Đảng viên:", placeholder="Ví dụ: 0965...")
        if st.form_submit_button("ĐĂNG NHẬP"):
            try:
                # Đọc dữ liệu từ Sheets (ép kiểu string để không mất số 0)
                df = pd.read_csv(CSV_URL, dtype=str)
                target = clean_num(sdt_nhap)
                
                match_row = None
                # Duyệt qua từng hàng và từng ô để tìm số điện thoại
                for _, row in df.iterrows():
                    for cell_value in row.values:
                        if target != "" and target == clean_num(cell_value):
                            match_row = row.to_dict()
                            break
                    if match_row: break
                
                if match_row:
                    # Tìm tên trong các cột
                    ten = "Đồng chí"
                    for k, v in match_row.items():
                        if any(x in str(k).lower() for x in ['họ tên', 'tên', 'hoten']):
                            ten = str(v)
                            break
                    st.session_state.auth = True
                    st.session_state.user = {"name": ten, "phone": sdt_nhap}
                    st.rerun()
                else:
                    st.error(f"❌ Số {sdt_nhap} chưa có trong danh sách. Đồng chí hãy thêm vào file Sheets rồi thử lại.")
            except:
                st.error("⚠️ Lỗi kết nối. Hãy đảm bảo file Sheets đã được 'Chia sẻ' quyền 'Bất kỳ ai có liên kết đều có thể xem'.")
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
            # Lấy giờ VN chuẩn
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            gio = datetime.now(tz).strftime("%H:%M:%S %d/%m/%Y")
            # Gửi dữ liệu về Script
            payload = {"sheetName": "NhatKyHop", "values": [gio, u['phone'], u['name'], "Có mặt"]}
            try:
                requests.post(SCRIPT_URL, data=json.dumps(payload))
                st.success(f"Đã ghi nhận điểm danh thành công!")
                st.balloons()
            except:
                st.error("Lỗi gửi dữ liệu điểm danh.")

    elif choice == "📊 QUẢN TRỊ" and is_admin:
        st.markdown("<h2 style='color: #d32f2f;'>🖥️ BẢNG ĐIỀU HÀNH</h2>", unsafe_allow_html=True)
        try:
            df_ds = pd.read_csv(CSV_URL)
            df_log = pd.read_csv(LOG_URL)
            st.metric("Tổng số Đảng viên", len(df_ds))
            st.metric("Số người đã điểm danh", df_log.iloc[:, 1].nunique() if not df_log.empty else 0)
            st.write("---")
            st.subheader("📋 Nhật ký mới nhất")
            st.dataframe(df_log.tail(10), use_container_width=True)
        except:
            st.info("Chưa có dữ liệu điểm danh trong trang 'NhatKyHop'.")
