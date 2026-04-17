import streamlit as st
import pandas as pd
import requests
import json
import base64
import time
import io
from datetime import datetime
from PIL import Image  # Thư viện để nén ảnh

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link Script của đồng chí đã gửi
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
        background: white; padding: 25px; border-radius: 12px;
        border-top: 5px solid #d32f2f;
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .section-title {
        color: #b71c1c; font-size: 18px; font-weight: 800;
        margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;
    }
    .stButton>button {
        background: #d32f2f; color: white; border-radius: 8px;
        font-weight: 600; width: 100%; height: 3.5em; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HÀM XỬ LÝ DỮ LIỆU & NÉN ẢNH
# ==========================================
def compress_image(uploaded_file):
    """Nén ảnh để tránh lỗi 'Payload too large' khi gửi sang Google Sheets"""
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((1024, 1024)) # Giới hạn chiều rộng tối đa 1024px
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=70, optimize=True) # Nén chất lượng còn 70%
    return buffer.getvalue()

def save_to_sheets(sheet_name, row_values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": row_values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=60)
        return res.status_code == 200
    except:
        return False

def get_data_fresh(url):
    try:
        r = requests.get(f"{url}&t={int(time.time())}", timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except:
        return pd.DataFrame()

# ==========================================
# 4. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown('<div class="feature-card" style="text-align:center; margin-top:50px;">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=70)
        st.subheader("HỆ THỐNG QUẢN TRỊ")
        with st.form("login"):
            u = st.text_input("Tên đăng nhập:")
            p = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("XÁC THỰC TRUY CẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Sai thông tin!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>DANH MỤC</h2>", unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["🔍 Tra cứu thông tin", "👤 Hồ sơ Đảng viên", "📂 Văn bản & Báo cáo"])
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- TAB 1: TRA CỨU ---
if menu == "🔍 Tra cứu thông tin":
    st.markdown('<div class="header-box"><h1>TRUNG TÂM TRA CỨU TỔNG HỢP</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    q = st.text_input("🔎 Nhập nội dung cần tìm kiếm:", placeholder="Tên Đảng viên, nội dung báo cáo, trích yếu...")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if q:
        with st.spinner("Đang lục tìm dữ liệu..."):
            url_hs = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"
            url_vb = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=VanBan"
            df_hs, df_vb = get_data_fresh(url_hs), get_data_fresh(url_vb)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-title">👤 HỒ SƠ ĐẢNG VIÊN</div>', unsafe_allow_html=True)
                if not df_hs.empty:
                    res = df_hs[df_hs.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                    st.dataframe(res, use_container_width=True)
            with c2:
                st.markdown('<div class="section-title">📂 VĂN BẢN/BÁO CÁO</div>', unsafe_allow_html=True)
                if not df_vb.empty:
                    res = df_vb[df_vb.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
                    st.dataframe(res, use_container_width=True)

# --- TAB 2: QUẢN LÝ ĐẢNG VIÊN ---
elif menu == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="header-box"><h1>DANH SÁCH ĐẢNG VIÊN</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📑 THÊM HỒ SƠ MỚI</div>', unsafe_allow_html=True)
    with st.form("form_dv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        ten = c1.text_input("Họ và tên:")
        cv = c2.text_input("Chức vụ:")
        gc = st.text_area("Ghi chú hoàn cảnh/đặc điểm:")
        if st.form_submit_button("💾 LƯU VÀO HỆ THỐNG"):
            if ten:
                row = [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc]
                if save_to_sheets("HoSo", row):
                    st.success(f"✅ Đã lưu hồ sơ đồng chí {ten} thành công!")
                else: st.error("❌ Lỗi kết nối Script!")
            else: st.warning("Vui lòng nhập tên Đảng viên.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: KHO VĂN BẢN ---
elif menu == "📂 Văn bản & Báo cáo":
    st.markdown('<div class="header-box"><h1>KHO VĂN BẢN & BÁO CÁO</h1></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📤 TẢI LÊN & LƯU TRỮ VĂN BẢN</div>', unsafe_allow_html=True)
    with st.form("form_vb", clear_on_submit=True):
        col1, col2 = st.columns(2)
        loai = col1.selectbox("Phân loại văn bản:", ["Văn bản cấp trên", "Công văn chi bộ", "Báo cáo nội bộ"])
        trich_yeu = col2.text_input("Trích yếu nội dung (Ghi tóm tắt):")
        file = st.file_uploader("📷 Chụp ảnh văn bản hoặc chọn ảnh:", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("💾 XÁC NHẬN LƯU VĂN BẢN"):
            if trich_yeu and file:
                with st.spinner("Đang nén ảnh và lưu trữ..."):
                    img_compressed = compress_image(file)
                    img_base64 = base64.b64encode(img_compressed).decode('utf-8')
                    row = [datetime.now().strftime("%d/%m/%Y %H:%M"), loai, trich_yeu, img_base64]
                    if save_to_sheets("VanBan", row):
                        st.success("✅ Văn bản đã được lưu vào kho lưu trữ!")
                    else: st.error("❌ Lỗi upload! Vui lòng kiểm tra quyền Script.")
            else: st.warning("Đồng chí cần nhập trích yếu và chọn ảnh văn bản.")
    st.markdown('</div>', unsafe_allow_html=True)
