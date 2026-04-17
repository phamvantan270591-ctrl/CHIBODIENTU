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

# Hàm tải dữ liệu
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
    st.title("🇻🇳 ĐĂNG NHẬP")
    u, p = st.text_input("Tên đăng nhập"), st.text_input("Mật khẩu", type="password")
    if st.button("VÀO APP"):
        if u == "Admin" and p == "Tan@753496": st.session_state.auth = True; st.rerun()
    st.stop()

menu = st.sidebar.radio("CHỨC NĂNG", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản", "🖼 Kho văn bản ảnh"])

# --- 1. QUẢN LÝ HỒ SƠ ---
if menu == "👤 Hồ sơ Đảng viên":
    st.header("👤 HỒ SƠ ĐẢNG VIÊN")
    with st.form("f1", clear_on_submit=True):
        ten, cv, gc = st.text_input("Họ tên"), st.text_input("Chức vụ"), st.text_area("Ghi chú")
        if st.form_submit_button("LƯU HỒ SƠ"):
            if ten:
                save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc])
                st.success("Đã lưu!"); time.sleep(1); st.rerun()
    st.dataframe(load_data("HoSo"), use_container_width=True)

# --- 2. LƯU VĂN BẢN ---
elif menu == "📤 Lưu văn bản":
    st.header("📤 LƯU VĂN BẢN MỚI")
    with st.form("f2", clear_on_submit=True):
        m1 = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m2 = st.selectbox("Loại:", ["Quyết định", "Công văn", "Kế hoạch", "Khác"]) if m1 == "Văn bản cấp trên" else m1
        ty = st.text_input("Trích yếu nội dung:")
        anh = st.file_uploader("Chọn ảnh:", type=['jpg','png','jpeg'])
        if st.form_submit_button("XÁC NHẬN LƯU"):
            if ty and anh:
                img = Image.open(anh).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=50)
                txt = base64.b64encode(buf.getvalue()).decode()
                if save_data("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M"), m1, m2, ty, txt]):
                    st.success("Đã lưu văn bản thành công!")
            else: st.warning("Vui lòng điền đủ thông tin!")

# --- 3. KHO VĂN BẢN (GIAO DIỆN GỌN GÀNG, ẨN ẢNH) ---
elif menu == "🖼 Kho văn bản ảnh":
    st.header("🖼 KHO VĂN BẢN")
    df = load_data("VanBan")
    if df.empty:
        st.info("Chưa có dữ liệu.")
    else:
        # Ô tìm kiếm nhanh
        search = st.text_input("🔎 Tìm nhanh theo trích yếu:", "")
        if search:
            df = df[df.iloc[:, 3].str.contains(search, case=False)]

        tab1, tab2, tab3 = st.tabs(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        t_list = [tab1, tab2, tab3]
        m_list = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        
        for i, m in enumerate(m_list):
            with t_list[i]:
                sub_df = df[df.iloc[:, 1] == m]
                if sub_df.empty:
                    st.write("Trống.")
                else:
                    for idx, row in sub_df.iterrows():
                        # Mỗi văn bản nằm trong 1 container gọn gàng
                        with st.container():
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                st.markdown(f"**📄 {row.iloc[3]}**")
                                st.caption(f"📅 {row.iloc[0]} | Loại: {row.iloc[2]}")
                            with c2:
                                # Nút bấm để điều khiển việc hiện ảnh
                                show_key = f"show_{idx}"
                                if st.button("👁️ Xem ảnh", key=show_key):
                                    st.session_state[f"view_{idx}"] = True
                            
                            # Kiểm tra nếu người dùng đã nhấn xem ảnh
                            if st.session_state.get(f"view_{idx}", False):
                                try:
                                    ma_anh = str(row.iloc[-1]).strip()
                                    st.image(base64.b64decode(ma_anh), use_container_width=True)
                                    if st.button("❌ Ẩn ảnh", key=f"hide_{idx}"):
                                        st.session_state[f"view_{idx}"] = False
                                        st.rerun()
                                except:
                                    st.error("Không thể hiển thị ảnh.")
                            st.write("---")
