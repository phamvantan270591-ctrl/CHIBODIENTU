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

# Hàm lưu dữ liệu
def save_data(sheet_name, values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return res.status_code == 200
    except: return False

# Hàm tải dữ liệu (Tự động làm mới)
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

# MENU CHÍNH
menu = st.sidebar.radio("CHỨC NĂNG", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản", "🖼 Kho văn bản ảnh"])

# --- 1. HỒ SƠ ĐẢNG VIÊN ---
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
    st.subheader("📋 Danh sách")
    st.dataframe(load_data("HoSo"), use_container_width=True)

# --- 2. LƯU VĂN BẢN (PHÂN LOẠI) ---
elif menu == "📤 Lưu văn bản":
    st.header("📤 LƯU VĂN BẢN THEO MỤC")
    with st.form("f2", clear_on_submit=True):
        muc_lon = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        loai_phu = ""
        if muc_lon == "Văn bản cấp trên":
            loai_phu = st.selectbox("Loại văn bản:", ["Quyết định", "Công văn", "Kế hoạch"])
        else:
            loai_phu = muc_lon
            
        trich_yeu = st.text_input("Trích yếu nội dung:")
        anh = st.file_uploader("Chọn ảnh:", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if trich_yeu and anh:
                with st.spinner("Đang nén ảnh..."):
                    img = Image.open(anh).convert("RGB")
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=50)
                    txt_anh = base64.b64encode(buf.getvalue()).decode()
                    # Cấu trúc: Ngày | Mục Lớn | Loại | Trích yếu | Mã ảnh
                    if save_data("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M"), muc_lon, loai_phu, trich_yeu, txt_anh]):
                        st.success("Đã lưu thành công!")
            else: st.warning("Điền thiếu thông tin!")

# --- 3. KHO VĂN BẢN (SỬA LỖI HIỂN THỊ) ---
elif menu == "🖼 Kho văn bản ảnh":
    st.header("🖼 KHO LƯU TRỮ VĂN BẢN")
    df_v = load_data("VanBan")
    
    if df_v.empty:
        st.info("Chưa có dữ liệu.")
    else:
        tab1, tab2, tab3 = st.tabs(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        
        danh_muc = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        cac_tab = [tab1, tab2, tab3]
        
        for i, ten_muc in enumerate(danh_muc):
            with cac_tab[i]:
                # Lọc đúng mục lớn (Cột thứ 2 - index 1)
                df_loc = df_v[df_v.iloc[:, 1] == ten_muc]
                if df_loc.empty:
                    st.write("Chưa có văn bản mục này.")
                else:
                    for idx, row in df_loc.iterrows():
                        # Tiêu đề: [Loại] - Trích yếu
                        with st.expander(f"📄 [{row.iloc[2]}] - {row.iloc[3]}"):
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                try:
                                    # Lấy cột cuối cùng chứa mã Base64
                                    ma_anh = str(row.iloc[-1]).strip()
                                    if len(ma_anh) > 100: # Kiểm tra xem có phải mã ảnh không
                                        st.image(base64.b64decode(ma_anh), use_container_width=True)
                                    else:
                                        st.error("Dữ liệu ảnh không hợp lệ.")
                                except Exception as e:
                                    st.error("Không thể giải mã ảnh.")
                            with c2:
                                st.write(f"📅 **Ngày:** {row.iloc[0]}")
                                st.write(f"📝 **Nội dung:** {row.iloc[3]}")
