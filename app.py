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

# CSS để giao diện chuyên nghiệp hơn
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;
    }
    .feature-card {
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #d32f2f; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HÀM XỬ LÝ DỮ LIỆU
# ==========================================
def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((800, 800)) 
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=60, optimize=True)
    return buffer.getvalue()

def save_to_sheets(sheet_name, row_values):
    try:
        payload = {"method": "append_row", "sheetName": sheet_name, "values": row_values}
        res = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=60)
        return res.status_code == 200
    except: return False

def get_data_fresh(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"
    try:
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        return pd.read_csv(io.StringIO(r.text), dtype=str).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 3. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown('<div class="feature-card" style="text-align:center; margin-top:50px;">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hammer_and_sickle.svg/1200px-Hammer_and_sickle.svg.png", width=70)
        st.subheader("HỆ THỐNG QUẢN TRỊ")
        with st.form("login"):
            u = st.text_input("Tên đăng nhập:")
            p = st.text_input("Mật khẩu:", type="password")
            if st.form_submit_button("ĐĂNG NHẬP"):
                if u == "Admin" and p == "Tan@753496":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Sai thông tin!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#d32f2f;'>DANH MỤC</h2>", unsafe_allow_html=True)
    menu = st.radio("CHỨC NĂNG:", ["👤 Hồ sơ Đảng viên", "📤 Lưu văn bản mới", "🖼 Xem kho văn bản ảnh"])
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- TAB 1: QUẢN LÝ ĐẢNG VIÊN ---
if menu == "👤 Hồ sơ Đảng viên":
    st.markdown('<div class="header-box"><h1>HỒ SƠ ĐẢNG VIÊN</h1></div>', unsafe_allow_html=True)
    with st.form("form_dv", clear_on_submit=True):
        c1, c2 = st.columns(2)
        ten = c1.text_input("Họ và tên:")
        cv = c2.text_input("Chức vụ:")
        gc = st.text_area("Ghi chú:")
        if st.form_submit_button("💾 LƯU HỒ SƠ"):
            if ten:
                if save_to_sheets("HoSo", [datetime.now().strftime("%d/%m/%Y %H:%M"), ten, cv, gc]):
                    st.success(f"Đã lưu hồ sơ đồng chí {ten}")
                else: st.error("Lỗi kết nối!")
            else: st.warning("Nhập tên Đảng viên.")

# --- TAB 2: LƯU VĂN BẢN MỚI ---
elif menu == "📤 Lưu văn bản mới":
    st.markdown('<div class="header-box"><h1>LƯU TRỮ VĂN BẢN</h1></div>', unsafe_allow_html=True)
    with st.form("form_vb", clear_on_submit=True):
        loai = st.selectbox("Loại:", ["Cấp trên", "Chi bộ", "Báo cáo"])
        trich_yeu = st.text_input("Trích yếu nội dung (Ghi rõ để dễ tìm):")
        file = st.file_uploader("Chụp ảnh hoặc chọn ảnh:", type=['jpg','png','jpeg'])
        if st.form_submit_button("💾 XÁC NHẬN LƯU"):
            if trich_yeu and file:
                with st.spinner("Đang xử lý ảnh..."):
                    img_compressed = compress_image(file)
                    img_base64 = base64.b64encode(img_compressed).decode('utf-8')
                    row = [datetime.now().strftime("%d/%m/%Y %H:%M"), loai, trich_yeu, img_base64]
                    if save_to_sheets("VanBan", row):
                        st.success("Đã lưu văn bản thành công!")
                    else: st.error("Lỗi upload!")
            else: st.warning("Điền đủ thông tin và chọn ảnh.")

# --- TAB 3: XEM KHO VĂN BẢN (GIẢI MÃ KÝ TỰ THÀNH ẢNH) ---
elif menu == "🖼 Xem kho văn bản ảnh":
    st.markdown('<div class="header-box"><h1>KHO VĂN BẢN ĐÃ LƯU</h1></div>', unsafe_allow_html=True)
    with st.spinner("Đang tải danh sách..."):
        df_vb = get_data_fresh("VanBan")
    
    if not df_vb.empty:
        # Lấy cột trích yếu (thường là cột thứ 3, chỉ số 2)
        list_vb = df_vb.iloc[:, 2].tolist() 
        chon_vb = st.selectbox("Chọn văn bản muốn xem lại ảnh:", ["-- Chọn văn bản --"] + list_vb)
        
        if chon_vb != "-- Chọn văn bản --":
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            # Tìm dòng dữ liệu tương ứng
            row_data = df_vb[df_vb.iloc[:, 2] == chon_vb].iloc[0]
            # Cột cuối cùng (chỉ số 3) là chuỗi ký tự dài
            img_code = row_data.iloc[3] 
            
            try:
                # Chuyển dãy ký tự ngược lại thành ảnh
                img_bytes = base64.b64decode(img_code)
                st.image(img_bytes, caption=f"Văn bản: {chon_vb}", use_container_width=True)
                st.write(f"📅 Ngày lưu: {row_data.iloc[0]}")
                st.write(f"📁 Loại: {row_data.iloc[1]}")
            except:
                st.error("Dữ liệu ảnh bị lỗi hoặc không đầy đủ.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Chưa có văn bản nào được lưu trữ.")
