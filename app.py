import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io
from datetime import datetime
from PIL import Image

# 1. CẤU HÌNH
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

# Hàm hỗ trợ
def save_data(sheet_name, values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return res.status_code == 200
    except: return False

def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

# Đăng nhập
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🇻🇳 ĐĂNG NHẬP HỆ THỐNG")
    u = st.text_input("Tên đăng nhập")
    p = st.text_input("Mật khẩu", type="password")
    if st.button("VÀO APP"):
        if u == "Admin" and p == "Tan@753496":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Sai tài khoản!")
    st.stop()

# MENU
menu = st.sidebar.radio("CHỨC NĂNG", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản", "🖼 Kho văn bản ảnh"])

# --- PHẦN 1: HỒ SƠ ĐẢNG VIÊN ---
if menu == "👤 Hồ sơ Đảng viên":
    st.header("👤 QUẢN LÝ HỒ SƠ")
    with st.form("f1", clear_on_submit=True):
        ten = st.text_input("Họ tên")
        chucvu = st.text_input("Chức vụ")
        ghichu = st.text_area("Ghi chú")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if ten:
                if save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, chucvu, ghichu]):
                    st.success("Đã lưu!"); time.sleep(1); st.rerun()
            else: st.warning("Nhập tên!")
    df_hs = load_data("HoSo")
    if not df_hs.empty: st.dataframe(df_hs, use_container_width=True)

# --- PHẦN 2: LƯU VĂN BẢN (PHÂN LOẠI MỚI) ---
elif menu == "📤 Lưu văn bản":
    st.header("📤 LƯU VĂN BẢN THEO MỤC")
    with st.form("f2", clear_on_submit=True):
        # Chọn mục lớn
        muc_lon = st.selectbox("Chọn mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        
        # Nếu là văn bản cấp trên thì hiện thêm mục con
        loai_chi_tiet = ""
        if muc_lon == "Văn bản cấp trên":
            loai_chi_tiet = st.selectbox("Loại văn bản:", ["Quyết định", "Công văn", "Kế hoạch"])
        else:
            loai_chi_tiet = muc_lon
            
        trich_yeu = st.text_input("Trích yếu nội dung:")
        anh = st.file_uploader("Chọn ảnh:", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if trich_yeu and anh:
                with st.spinner("Đang xử lý..."):
                    img = Image.open(anh).convert("RGB")
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=50)
                    txt_anh = base64.b64encode(buf.getvalue()).decode()
                    # Lưu vào Sheets: [Ngày, Mục lớn, Loại chi tiết, Trích yếu, Mã ảnh]
                    data = [datetime.now().strftime("%d/%m/%Y %H:%M"), muc_lon, loai_chi_tiet, trich_yeu, txt_anh]
                    if save_data("VanBan", data):
                        st.success("Đã lưu thành công!")
            else: st.warning("Vui lòng điền đủ thông tin!")

# --- PHẦN 3: KHO VĂN BẢN ẢNH (BỐ CỤC MỚI) ---
elif menu == "🖼 Kho văn bản ảnh":
    st.header("🖼 KHO LƯU TRỮ VĂN BẢN")
    df_v = load_data("VanBan")
    
    if df_v.empty:
        st.info("Chưa có dữ liệu.")
    else:
        # Lọc theo mục lớn để dễ tìm
        loc_muc = st.tabs(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        
        for i, ten_muc in enumerate(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]):
            with loc_muc[i]:
                df_loc = df_v[df_v.iloc[:, 1] == ten_muc]
                if df_loc.empty:
                    st.write("Trống.")
                else:
                    for index, row in df_loc.iterrows():
                        with st.expander(f"[{row.iloc[2]}] - {row.iloc[3]}"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                try:
                                    st.image(base64.b64decode(row.iloc[4]), use_container_width=True)
                                except: st.error("Lỗi ảnh")
                            with col2:
                                st.write(f"📅 **Ngày lưu:** {row.iloc[0]}")
                                st.write(f"📁 **Phân loại:** {row.iloc[2]}")
                                st.write(f"📝 **Trích yếu:** {row.iloc[3]}")
