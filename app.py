import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io
from datetime import datetime
from PIL import Image

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link Script đồng chí đã gửi
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

# --- HÀM HỖ TRỢ DỮ LIỆU ---
def save_to_sheets(sheet_name, row_values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": row_values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return res.status_code == 200
    except: return False

def get_data_fresh(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60)
    return buffer.getvalue()

# ==========================================
# 2. XỬ LÝ ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>🇻🇳 HỆ THỐNG QUẢN TRỊ</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Tên đăng nhập")
            pwd = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("VÀO HỆ THỐNG"):
                if user == "Admin" and pwd == "Tan@753496":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Sai mật khẩu!")
    st.stop()

# ==========================================
# 3. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP)
# ==========================================
st.sidebar.title("DANH MỤC")
menu = st.sidebar.radio("Chọn chức năng:", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản mới", "🖼 Xem ảnh văn bản"])

if st.sidebar.button("Đăng xuất"):
    st.session_state.auth = False
    st.rerun()

# --- TRANG 1: HỒ SƠ ĐẢNG VIÊN ---
if menu == "👤 Hồ sơ Đảng viên":
    st.header("👤 QUẢN LÝ HỒ SƠ ĐẢNG VIÊN")
    
    # Form thêm mới
    with st.expander("➕ Thêm hồ sơ Đảng viên mới", expanded=True):
        with st.form("form_dv", clear_on_submit=True):
            ten = st.text_input("Họ và tên")
            cv = st.text_input("Chức vụ")
            gc = st.text_area("Ghi chú")
            if st.form_submit_button("LƯU HỒ SƠ"):
                if ten:
                    if save_to_sheets("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc]):
                        st.success("Đã lưu thành công!")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Lỗi gửi dữ liệu!")
                else: st.warning("Hãy nhập tên!")

    # Bảng danh sách
    st.subheader("📋 Danh sách Đảng viên hiện có")
    df_hs = get_data_fresh("HoSo")
    if not df_hs.empty:
        st.dataframe(df_hs, use_container_width=True)
    else:
        st.info("Đang tải danh sách hoặc chưa có dữ liệu...")

# --- TRANG 2: LƯU VĂN BẢN ---
elif menu == "📤 Lưu văn bản mới":
    st.header("📤 LƯU TRỮ VĂN BẢN (CHỤP ẢNH)")
    with st.form("form_vb", clear_on_submit=True):
        trich_yeu = st.text_input("Trích yếu nội dung văn bản")
        file = st.file_uploader("Chọn ảnh văn bản", type=['jpg','png','jpeg'])
        if st.form_submit_button("XÁC NHẬN LƯU"):
            if trich_yeu and file:
                with st.spinner("Đang tải ảnh..."):
                    img_b64 = base64.b64encode(compress_image(file)).decode()
                    if save_to_sheets("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M
