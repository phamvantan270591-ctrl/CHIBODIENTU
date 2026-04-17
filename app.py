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
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

# Tùy chỉnh giao diện
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .stExpander { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
def save_data(sheet_name, values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return res.status_code == 200
    except: return False

def load_data(sheet_name):
    # Thêm tham số t để phá cache của Google, đảm bảo lấy dữ liệu mới nhất
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

def compress_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((800, 800))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=50)
    return base64.b64encode(buf.getvalue()).decode()

# ==========================================
# 2. KIỂM TRA ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🇻🇳 HỆ THỐNG QUẢN TRỊ ĐẢNG VỤ")
    with st.container():
        u = st.text_input("Tên đăng nhập")
        p = st.text_input("Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Sai thông tin đăng nhập!")
    st.stop()

# ==========================================
# 3. MENU VÀ ĐIỀU HƯỚNG
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=80)
    st.title("DANH MỤC")
    menu = st.radio("Chức năng chính:", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản mới", "🖼 Kho văn bản ảnh"])
    st.write("---")
    if st.button("🔄 Làm mới dữ liệu"):
        st.rerun()
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- TRANG 1: HỒ SƠ ĐẢNG VIÊN ---
if menu == "👤 Hồ sơ Đảng viên":
    st.header("👤 QUẢN LÝ HỒ SƠ ĐẢNG VIÊN")
    with st.form("form_hoso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Họ và tên")
        role = col2.text_input("Chức vụ")
        note = st.text_area("Ghi chú thêm")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if name:
                if save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), name, role, note]):
                    st.success(f"Đã lưu hồ sơ đồng chí {name}")
                    time.sleep(1)
                    st.rerun()
            else: st.warning("Vui lòng nhập họ tên.")

    st.subheader("📋 Danh sách Đảng viên")
    df_hoso = load_data("HoSo")
    if not df_hoso.empty:
        st.dataframe(df_hoso, use_container_width=True)
    else: st.info("Chưa có dữ liệu hồ sơ.")

# --- TRANG 2: LƯU VĂN BẢN (PHÂN LOẠI 5 CỘT) ---
elif menu == "📤 Lưu văn bản mới":
    st.header("📤 LƯU TRỮ VĂN BẢN MỚI")
    with st.form("form_vanban", clear_on_submit=True):
        m1 = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        # Phân loại chi tiết cho văn bản cấp trên
        if m1 == "Văn bản cấp trên":
            m2 = st.selectbox("Loại văn bản:", ["Quyết định", "Công văn", "Kế hoạch"])
        else:
            m2 = m1
            
        ty = st.text_input("Trích yếu nội dung (Tìm kiếm theo tên này):")
        file = st.file_uploader("Chụp hoặc chọn ảnh văn bản:", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if ty and file:
                with st.spinner("Đang mã hóa và gửi dữ liệu..."):
                    img_code = compress_image(file)
                    ngay = datetime.now().strftime("%d/%m/%Y %H:%M")
                    if save_data("VanBan", [ngay, m1, m2, ty, img_code]):
                        st.success("Đã lưu văn bản thành công vào Sheets!")
                    else: st.error("Lỗi kết nối máy chủ!")
            else: st.warning("Vui lòng điền trích yếu và chọn ảnh.")

# --- TRANG 3: KHO VĂN BẢN (GIAO DIỆN GỌN GÀNG, ẨN ẢNH) ---
elif menu == "🖼 Kho văn bản ảnh":
    st.header("🖼 KHO LƯU TRỮ VĂN BẢN")
    
    # Nút tải lại nhanh
    if st.button("🔃 Tải danh sách mới nhất"):
        st.rerun()

    df_vb = load_data("VanBan")
    if df_vb.empty:
        st.info("Kho dữ liệu đang trống.")
    else:
        # Tìm kiếm
        search = st.text_input("🔎 Tìm kiếm theo trích yếu:", "")
        if search:
            df_vb = df_vb[df_vb.iloc[:, 3].str.contains(search, case=False)]

        # Phân loại theo Tabs
        tab1, tab2, tab3 = st.tabs(["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m_list = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        t_list = [tab1, tab2, tab3]

        for i, muc_ten in enumerate(m_list):
            with t_list[i]:
                # Lọc dữ liệu theo cột Mục chính (index 1)
                sub_df = df_vb[df_vb.iloc[:, 1] == muc_ten]
                if sub_df.empty:
                    st.write("Chưa có dữ liệu trong mục này.")
                else:
                    for idx, row in sub_df.iterrows():
                        with st.container():
                            c_info, c_btn = st.columns([4, 1])
                            with c_info:
                                st.markdown(f"**📄 {row.iloc[3]}**")
                                st.caption(f"📅 {row.iloc[0]} | Loại: {row.iloc[2]}")
                            with c_btn:
                                # Sử dụng session_state để kiểm soát ẩn/hiện ảnh riêng biệt
                                view_key = f"v_{idx}"
                                if st.button("👁️ Xem", key=f"btn_{idx}"):
                                    st.session_state[view_key] = True
                            
                            # Hiển thị ảnh nếu được yêu cầu
                            if st.session_state.get(view_key, False):
                                try:
                                    # Lấy cột cuối cùng (Mã ảnh)
                                    img_data = base64.b64decode(str(row.iloc[-1]).strip())
                                    st.image(img_data, use_container_width=True)
                                    if st.button("❌ Ẩn", key=f"hide_{idx}"):
                                        st.session_state[view_key] = False
                                        st.rerun()
                                except:
                                    st.error("Dữ liệu ảnh bị lỗi.")
                            st.write("---")
