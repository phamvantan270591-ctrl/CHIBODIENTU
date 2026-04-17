import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link Script đồng chí vừa cung cấp
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwd_94ZlYdo3qJ_qS-Ou8OJLPRrM6gyG3kSeJVK8Mo3U3bLk-iqw3w8CV4Gci3D1vI4/exec"

st.set_page_config(page_title="QUẢN TRỊ ĐẢNG VỤ CÁ NHÂN", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GIAO DIỆN CHUYÊN NGHIỆP (CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 25px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
    }
    .feature-card {
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #d32f2f;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 8px;
        font-weight: 600; width: 100%; height: 3em; border: none;
    }
    .stButton>button:hover { background: #ff1744; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HÀM GỬI DỮ LIỆU VỀ GOOGLE SHEETS
# ==========================================
def save_data(sheet_name, row_values):
    try:
        payload = {
            "method": "append_row",
            "sheetName": sheet_name,
            "values": row_values
        }
        response = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=30)
        return response.status_code == 200
    except:
        return False

def get_data_fresh(url):
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=10)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 4. KIỂM TRA ĐĂNG NHẬP
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<br><br>', unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
            <div style="background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png" width="70">
                <h2 style="color: #b71c1c; margin-top: 15px;">HỆ THỐNG QUẢN TRỊ</h2>
                <p style="color: #666;">Dành riêng cho Quản trị viên</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("👤 Tên đăng nhập:")
            p = st.text_input("🔑 Mật khẩu:", type="password")
            if st.form_submit_button("XÁC THỰC"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Thông tin đăng nhập không chính xác!")
    st.stop()

# ==========================================
# 5. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>DANH MỤC</h2>", unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["🔍 Tra cứu & Tìm kiếm", "👤 Hồ sơ Đảng viên", "📂 Kho văn bản & Báo cáo"])
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.authenticated = False
        st.rerun()

# --- TAB 1: TRA CỨU ---
if menu == "🔍 Tra cứu & Tìm kiếm":
    st.markdown('<div class="header-box"><h1>TRUNG TÂM TRA CỨU</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    q = st.text_input("🔎 Nhập từ khóa cần tìm:", placeholder="Tên Đảng viên, nội dung công văn...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        with st.spinner("Đang lục tìm dữ liệu..."):
            url_hs = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
            url_vb = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"
            df_hs = get_data_fresh(url_hs)
            df_vb = get_data_fresh(url_vb)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Kết quả trong Hồ sơ:**")
                if not df_hs.empty:
                    res = df_hs[df_hs.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                    st.dataframe(res, use_container_width=True)
            with c2:
                st.markdown("**Kết quả trong Văn bản:**")
                if not df_vb.empty:
                    res = df_vb[df_vb.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                    st.dataframe(res, use_container_width=True)

# --- TAB 2: QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="header-box"><h1>HỒ SƠ ĐẢNG VIÊN</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    with st.form("form_dv", clear_on_submit=True):
        st.markdown("**Thêm hồ sơ mới**")
        c1, c2 = st.columns(2)
        ten = c1.text_input("Họ và tên:")
        cv = c2.text_input("Chức vụ:")
        gc = st.text_area("Ghi chú đặc điểm:")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if ten:
                row = [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc]
                if save_data("HoSo", row):
                    st.success(f"Đã lưu hồ sơ đồng chí {ten}!")
                    time.sleep(1); st.rerun()
                else: st.error("Lỗi kết nối Script!")
            else: st.warning("Vui lòng nhập tên.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: VĂN BẢN ---
elif menu == "📂 Kho văn bản & Báo cáo":
    st.markdown('<div class="header-box"><h1>KHO VĂN BẢN & BÁO CÁO</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    with st.form("form_vb", clear_on_submit=True):
        st.markdown("**Lưu văn bản mới (Chụp ảnh)**")
        loai = st.selectbox("Loại:", ["Cấp trên", "Chi bộ", "Báo cáo"])
        trich_yeu = st.text_input("Trích yếu nội dung:")
        file = st.file_uploader("Chọn ảnh văn bản:", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU TRỮ"):
            if trich_yeu and file:
                with st.spinner("Đang tải ảnh lên..."):
                    img_base64 = base64.b64encode(file.getvalue()).decode('utf-8')
                    row = [datetime.now().strftime("%d/%m/%Y %H:%M"), loai, trich_yeu, img_base64]
                    if save_data("VanBan", row):
                        st.success("Đã lưu văn bản thành công!")
                        time.sleep(1); st.rerun()
                    else: st.error("Lỗi không lưu được!")
            else: st.warning("Thiếu trích yếu hoặc ảnh.")
    st.markdown('</div>', unsafe_allow_html=True)
