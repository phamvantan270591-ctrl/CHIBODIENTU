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
# 1. CẤU HÌNH & CSS TÙY CHỈNH
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    /* Ô tiêu đề đỏ đặc trưng */
    .header-red {
        background-color: #d32f2f;
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Thiết kế 6 khối nút bấm cân đối */
    div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        height: 150px !important; 
        width: 100% !important;
        font-size: 20px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        border: 2px solid #1b5e20 !important;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        white-space: pre-wrap; /* Hỗ trợ xuống dòng trong nút */
    }
    
    /* Hiệu ứng khi di chuột vào nút */
    div.stButton > button:hover {
        background-color: #1b5e20 !important;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    
    /* Nút Đăng xuất màu xám đậm để phân biệt */
    div.stButton > button[kind="secondary"] {
        background-color: #455a64 !important;
        border-color: #263238 !important;
    }

    .content-box {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border-top: 8px solid #d32f2f;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
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
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. QUẢN LÝ TRẠNG THÁI & ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False
if 'page' not in st.session_state: st.session_state.page = "home"

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.write("##")
        st.markdown('<div style="background-color:white; padding:40px; border-radius:20px; border:4px solid #d32f2f; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#d32f2f;'>🇻🇳 ĐĂNG NHẬP</h1>", unsafe_allow_html=True)
        user = st.text_input("Tài khoản quản trị")
        pwd = st.text_input("Mật khẩu hệ thống", type="password")
        if st.button("VÀO HỆ THỐNG"):
            if user == "Admin" and pwd == "Tan@753496":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Thông tin đăng nhập không chính xác!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. MENU CHÍNH (6 KHỐI CÂN ĐỐI)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="header-red"><h1>HỆ THỐNG QUẢN TRỊ ĐẢNG VỤ</h1></div>', unsafe_allow_html=True)
    
    # Hàng 1
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👤\nHỒ SƠ\nĐẢNG VIÊN"):
            st.session_state.page = "hoso"; st.rerun()
    with c2:
        if st.button("📤\nLƯU VĂN BẢN\nMỚI"):
            st.session_state.page = "luu_vb"; st.rerun()
    with c3:
        if st.button("🖼\nKHO ẢNH\nVĂN BẢN"):
            st.session_state.page = "kho_anh"; st.rerun()

    # Hàng 2
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🚩\nHOẠT ĐỘNG\nCHI BỘ"):
            st.session_state.page = "hoat_dong"; st.rerun()
    with c5:
        if st.button("⏰\nNHẮC VIỆC\nCẦN LÀM"):
            st.session_state.page = "nhac_viec"; st.rerun()
    with c6:
        if st.button("🚪\nĐĂNG XUẤT\nTHOÁT APP", type="secondary"):
            st.session_state.auth = False; st.rerun()

# --- NÚT QUAY LẠI CHUNG ---
def quay_lai_home():
    if st.button("⬅️ QUAY LẠI MENU CHÍNH"):
        st.session_state.page = "home"; st.rerun()

# ==========================================
# 4. CHI TIẾT CÁC TRANG CHỨC NĂNG
# ==========================================

# --- TRANG HỒ SƠ ---
if st.session_state.page == "hoso":
    st.markdown('<div class="header-red"><h2>HỒ SƠ ĐẢNG VIÊN</h2></div>', unsafe_allow_html=True)
    quay_lai_home()
    with st.form("f_hoso", clear_on_submit=True):
        t = st.text_input("Họ và tên")
        c = st.text_input("Chức vụ")
        g = st.text_area("Ghi chú")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if t:
                save_data("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), t, c, g])
                st.success("Đã lưu!")
    st.dataframe(load_data("HoSo"), use_container_width=True)

# --- TRANG LƯU VĂN BẢN ---
elif st.session_state.page == "luu_vb":
    st.markdown('<div class="header-red"><h2>LƯU VĂN BẢN MỚI</h2></div>', unsafe_allow_html=True)
    quay_lai_home()
    with st.form("f_vb", clear_on_submit=True):
        m1 = st.selectbox("Mục chính:", ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"])
        m2 = st.selectbox("Loại:", ["Quyết định", "Công văn", "Kế hoạch", "Khác"]) if m1 == "Văn bản cấp trên" else m1
        ty = st.text_input("Trích yếu nội dung:")
        file = st.file_uploader("Chọn ảnh văn bản:", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if ty and file:
                img = Image.open(file).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=50)
                txt = base64.b64encode(buf.getvalue()).decode()
                if save_data("VanBan", [datetime.now().strftime("%d/%m/%Y %H:%M"), m1, m2, ty, txt]):
                    st.success("Lưu thành công!")
            else: st.warning("Vui lòng điền đủ thông tin!")

# --- TRANG KHO ẢNH ---
elif st.session_state.page == "kho_anh":
    st.markdown('<div class="header-red"><h2>KHO VĂN BẢN ẢNH</h2></div>', unsafe_allow_html=True)
    quay_lai_home()
    df = load_data("VanBan")
    if df.empty:
        st.info("Chưa có văn bản nào.")
    else:
        tab1, tab2, tab3 = st.tabs(["Cấp trên", "Chi bộ", "Ảnh khác"])
        m_list = ["Văn bản cấp trên", "Văn bản Chi bộ", "Ảnh khác"]
        t_list = [tab1, tab2, tab3]
        for i, m in enumerate(m_list):
            with t_list[i]:
                sub_df = df[df.iloc[:, 1] == m]
                for idx, row in sub_df.iterrows():
                    with st.container():
                        col_t, col_b = st.columns([4, 1])
                        col_t.markdown(f"**📄 {row.iloc[3]}**\n\n📅 {row.iloc[0]} | {row.iloc[2]}")
                        if col_b.button("👁️ Xem", key=f"v_{idx}"):
                            st.session_state[f"img_{idx}"] = True
                        if st.session_state.get(f"img_{idx}", False):
                            st.image(base64.b64decode(str(row.iloc[-1]).strip()), use_container_width=True)
                            if st.button("❌ Ẩn", key=f"h_{idx}"):
                                st.session_state[f"img_{idx}"] = False
                                st.rerun()
                        st.write("---")

# --- CÁC TRANG ĐANG PHÁT TRIỂN ---
elif st.session_state.page == "hoat_dong":
    st.markdown('<div class="header-red"><h2>HOẠT ĐỘNG CHI BỘ</h2></div>', unsafe_allow_html=True)
    quay_lai_home()
    st.info("💡 Tính năng này dùng để ghi nhật ký họp và hoạt động chi bộ. Nội dung đang được thiết kế...")

elif st.session_state.page == "nhac_viec":
    st.markdown('<div class="header-red"><h2>NHẮC VIỆC CẦN LÀM</h2></div>', unsafe_allow_html=True)
    quay_lai_home()
    st.info("💡 Tính năng này giúp đồng chí quản lý các đầu việc cần làm trong tháng. Nội dung đang được thiết kế...")
