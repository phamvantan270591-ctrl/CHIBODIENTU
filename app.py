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

# 2. HÀM HỖ TRỢ
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

# 3. ĐĂNG NHẬP
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🇻🇳 ĐĂNG NHẬP HỆ THỐNG")
    with st.form("login"):
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("VÀO APP"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Sai tài khoản!")
    st.stop()

# 4. MENU
menu = st.sidebar.radio("CHỨC NĂNG", ["Hồ sơ Đảng viên", "Lưu văn bản", "Xem lại ảnh"])

if menu == "Hồ sơ Đảng viên":
    st.header("👤 QUẢN LÝ HỒ SƠ")
    with st.form("f1", clear_on_submit=True):
        ten = st.text_input("Họ tên")
        chucvu = st.text_input("Chức vụ")
        ghichu = st.text_area("Ghi chú")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if ten:
                ngay = datetime.now().strftime("%d/%m/%Y %H:%M")
                if save_data("HoSo", [ngay, ten, chucvu, ghichu]):
                    st.success("Đã lưu!")
                    time.sleep(1)
                    st.rerun()
            else: st.warning("Nhập tên!")
    
    st.subheader("📋 Danh sách hiện có")
    df_hs = load_data("HoSo")
    if not df_hs.empty:
        st.dataframe(df_hs, use_container_width=True)

elif menu == "Lưu văn bản":
    st.header("📤 LƯU VĂN BẢN (ẢNH)")
    with st.form("f2", clear_on_submit=True):
        trich_yeu = st.text_input("Trích yếu")
        anh = st.file_uploader("Chọn ảnh", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if trich_yeu and anh:
                with st.spinner("Đang nén và gửi..."):
                    img = Image.open(anh).convert("RGB")
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=50)
                    txt_anh = base64.b64encode(buf.getvalue()).decode()
                    ngay = datetime.now().strftime("%d/%m/%Y %H:%M")
                    if save_data("VanBan", [ngay, "Văn bản", trich_yeu, txt_anh]):
                        st.success("Đã lưu ảnh thành công!")
            else: st.warning("Điền đủ thông tin!")

elif menu == "Xem lại ảnh":
    st.header("🖼 KHO VĂN BẢN ẢNH")
    df_v = load_data("VanBan")
    
    if df_v.empty:
        st.info("Chưa có văn bản nào được lưu.")
    else:
        # 1. Ô tìm kiếm nhanh
        search = st.text_input("🔎 Tìm kiếm văn bản theo trích yếu:", "")
        
        # Lọc dữ liệu theo tìm kiếm
        if search:
            df_display = df_v[df_v.iloc[:, 2].str.contains(search, case=False)]
        else:
            df_display = df_v
            
        st.write(f"Tìm thấy {len(df_display)} văn bản.")
        st.write("---")

        # 2. Hiển thị dạng danh sách chuyên nghiệp
        for index, row in df_display.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📄 {row.iloc[2]}**")
                    st.caption(f"📅 Ngày lưu: {row.iloc[0]}")
                with col2:
                    # Dùng key duy nhất cho mỗi nút bấm
                    if st.button("👁️ Xem ảnh", key=f"btn_{index}"):
                        st.session_state.current_img = row.iloc[3]
                        st.session_state.current_title = row.iloc[2]
                st.write("---")

        # 3. Hiển thị ảnh khi bấm nút (Cửa sổ hiển thị)
        if 'current_img' in st.session_state:
            st.markdown(f"### 🖼 Đang xem: {st.session_state.current_title}")
            try:
                img_data = base64.b64decode(st.session_state.current_img)
                st.image(img_data, use_container_width=True)
                if st.button("❌ Đóng ảnh"):
                    del st.session_state.current_img
                    st.rerun()
            except:
                st.error("Lỗi dữ liệu ảnh!")
