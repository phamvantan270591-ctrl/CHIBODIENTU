import streamlit as st
import pandas as pd
import requests
import io
import time

# ==========================================
# 1. CẤU HÌNH HỆ THỐNG & CSS
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM" 
URL_HOSO = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=HoSo"

st.set_page_config(page_title="QUẢN LÝ ĐẢNG VIÊN ẤP 4", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* TIÊU ĐỀ ĐỎ GỌN NHỎ */
    .red-header {
        background-color: #cc0000; color: #ffcc00;
        padding: 15px; border-radius: 10px; text-align: center;
        font-weight: bold; border-bottom: 2px solid #ffcc00;
        margin-bottom: 20px; text-transform: uppercase;
    }

    /* KHỐI CHỮ NHẬT LỚN MÀU XANH LÁ (BAO NGOÀI) */
    .outer-green-box {
        background-color: #ffffff;
        border: 2px solid #2e7d32;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
    }

    /* KHỐI CHỮ NHẬT CON MÀU XANH LÁ (BÊN TRONG) */
    .inner-green-box {
        background-color: #f1f8e9;
        border: 1px solid #4caf50;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .green-label {
        color: #1b5e20; font-weight: bold; font-size: 1.1rem;
        margin-bottom: 5px; display: block;
    }

    /* NÚT BẤM TO DỄ CHẠM */
    .stButton > button {
        background-color: #2e7d32; color: white; border-radius: 12px;
        padding: 20px; font-weight: bold; width: 100%; border: none;
    }
    .stButton > button:hover { background-color: #1b5e20; }
    
    /* KHUNG CHI TIẾT TRẮNG TINH TẾ */
    .detail-card {
        background: white; padding: 15px; border-radius: 8px; 
        border-left: 5px solid #2e7d32; margin-top: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def load_data(url):
    try:
        r = requests.get(f"{url}&nocache={time.time()}", timeout=10)
        return pd.read_csv(io.StringIO(r.text)).fillna("")
    except: return pd.DataFrame()

# ==========================================
# 2. XỬ LÝ TRUY CẬP (ĐĂNG NHẬP)
# ==========================================
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="red-header">Hệ thống quản trị chi bộ Ấp 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="outer-green-box">', unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("Tài khoản:", value="Admin")
        p = st.text_input("Mật khẩu:", type="password")
        if st.form_submit_button("ĐĂNG NHẬP"):
            if u == "Admin" and p == "Tan@753496": 
                st.session_state.auth = True; st.rerun()
            else: st.error("Thông tin đăng nhập không chính xác!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. NỘI DUNG CHÍNH: QUẢN LÝ ĐẢNG VIÊN
# ==========================================
st.markdown('<div class="red-header">QUẢN TRỊ ĐẢNG VIÊN</div>', unsafe_allow_html=True)

# BẮT ĐẦU KHỐI LỚN MÀU XANH LÁ
st.markdown('<div class="outer-green-box">', unsafe_allow_html=True)
st.markdown('<span class="green-label">📂 HỒ SƠ CHI BỘ</span>', unsafe_allow_html=True)

# --- PHẦN 1: DANH SÁCH & CHI TIẾT ---
st.markdown('<div class="inner-green-box">', unsafe_allow_html=True)
st.markdown('<span class="green-label">📋 DANH SÁCH ĐẢNG VIÊN</span>', unsafe_allow_html=True)

df = load_data(URL_HOSO)
if not df.empty:
    # Lọc cột STT, Họ Tên, Ngày Sinh để hiển thị
    df_hien_thi = df.iloc[:, [0, 1, 2]]
    df_hien_thi.columns = ["STT", "HỌ VÀ TÊN", "NGÀY SINH"]
    
    st.write("*(Chạm vào từng người để xem chi tiết thông tin)*")
    
    # Bảng cho phép chọn dòng
    selection = st.dataframe(
        df_hien_thi, 
        use_container_width=True, 
        hide_index=True, 
        on_select="rerun", 
        selection_mode="single-row"
    )

    # Nếu có người được chọn -> Hiện khung chi tiết
    if len(selection.selection.rows) > 0:
        idx = selection.selection.rows[0]
        row_data = df.iloc[idx]
        st.markdown(f"""
            <div class="detail-card">
                <p style="color:#1b5e20; font-weight:bold; border-bottom:1px solid #eee; padding-bottom:5px;">THÔNG TIN CHI TIẾT</p>
                <p><b>Họ và tên:</b> {row_data.iloc[1]}</p>
                <p><b>Ngày sinh:</b> {row_data.iloc[2]}</p>
                <p><b>Chức vụ:</b> {row_data.iloc[3]}</p>
                <p><b>Ghi chú đặc điểm:</b> {row_data.iloc[4]}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Đang kết nối dữ liệu...")
st.markdown('</div>', unsafe_allow_html=True)

# --- PHẦN 2: THÊM ĐẢNG VIÊN ---
st.markdown('<div class="inner-green-box">', unsafe_allow_html=True)
st.markdown('<span class="green-label">➕ THÊM ĐẢNG VIÊN MỚI</span>', unsafe_allow_html=True)
with st.form("form_add_dv", clear_on_submit=True):
    new_name = st.text_input("Họ và tên:")
    new_date = st.text_input("Ngày tháng năm sinh:")
    new_pos = st.text_input("Chức vụ:")
    new_note = st.text_area("Ghi chú:")
    
    if st.form_submit_button("XÁC NHẬN LƯU HỒ SƠ"):
        if new_name:
            st.success(f"Đã ghi nhận Đảng viên: {new_name}")
            # Ở bước sau ta sẽ thêm lệnh ghi vào Google Sheets tại đây
        else:
            st.warning("Vui lòng nhập họ tên Đảng viên.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Kết thúc khối lớn

# NÚT THOÁT HỆ THỐNG
if st.button("🚪 THOÁT PHẦN MỀM"):
    st.session_state.auth = False
    st.rerun()
