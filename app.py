import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io

# ==========================================
# 1. THÔNG SỐ CẤU HÌNH (ĐỒNG CHÍ THAY LINK SCRIPT CỦA MÌNH)
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link Script phải được Triển khai ở chế độ "Anyone" (Bất kỳ ai)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"

st.set_page_config(page_title="HỆ THỐNG QUẢN TRỊ NỘI BỘ", layout="wide")

# ==========================================
# 2. HÀM XỬ LÝ CHUYỂN ĐỔI ẢNH ĐỂ LƯU
# ==========================================
def upload_to_gsheet(sheet_name, row_data):
    try:
        payload = {
            "sheetName": sheet_name,
            "values": row_data,
            "method": "append_row" # Lệnh bảo Script thêm một dòng mới
        }
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=20)
        return res.status_code == 200
    except:
        return False

# ==========================================
# 3. GIAO DIỆN ĐĂNG NHẬP (GIỮ NGUYÊN)
# ==========================================
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>🇻🇳 QUẢN TRỊ NỘI BỘ</h2>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Tên đăng nhập:")
        p = st.text_input("Mật khẩu:", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.admin_auth = True
                st.rerun()
            else: st.error("Sai thông tin!")
    st.stop()

# ==========================================
# 4. GIAO DIỆN CHỨC NĂNG
# ==========================================
menu = st.sidebar.radio("CHỨC NĂNG", ["👤 Đảng viên", "📂 Văn bản & Báo cáo"])

# --- PHẦN QUẢN LÝ VĂN BẢN (CÓ CHỨC NĂNG LƯU) ---
if menu == "📂 Văn bản & Báo cáo":
    st.header("📤 Lưu trữ Văn bản & Báo cáo")
    
    with st.form("form_upload", clear_on_submit=True):
        col1, col2 = st.columns(2)
        loai_vb = col1.selectbox("Loại văn bản:", ["Cấp trên", "Chi bộ", "Báo cáo"])
        trich_yeu = col2.text_input("Trích yếu nội dung:")
        ngay_luu = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        file = st.file_uploader("Chụp ảnh văn bản hoặc chọn tệp:", type=['jpg', 'png', 'jpeg'])
        
        submit = st.form_submit_button("💾 XÁC NHẬN LƯU VÀO HỆ THỐNG")
        
        if submit:
            if trich_yeu and file:
                with st.spinner('Đang mã hóa và gửi dữ liệu...'):
                    # Chuyển ảnh sang chuỗi văn bản để gửi đi
                    bytes_data = file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    # Chuẩn bị dòng dữ liệu để ghi vào Sheets (Cột: Ngày, Loại, Trích yếu, Dữ liệu ảnh)
                    row = [ngay_luu, loai_vb, trich_yeu, base64_image]
                    
                    if upload_to_gsheet("VanBan", row):
                        st.success("✅ Đã lưu thành công vào Google Sheets!")
                    else:
                        st.error("❌ Lỗi kết nối! Hãy kiểm tra lại SCRIPT_URL hoặc quyền truy cập Apps Script.")
            else:
                st.warning("Đồng chí cần nhập trích yếu và chọn ảnh trước.")

# --- PHẦN QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Đảng viên":
    st.header("👤 Hồ sơ Đảng viên")
    with st.form("form_dv", clear_on_submit=True):
        ten = st.text_input("Họ và tên:")
        cv = st.text_input("Chức vụ:")
        luu_dv = st.form_submit_button("Lưu hồ sơ")
        if luu_dv:
            if upload_to_gsheet("HoSo", [ten, cv, datetime.now().strftime("%d/%m/%Y")]):
                st.success("Đã lưu hồ sơ Đảng viên!")
