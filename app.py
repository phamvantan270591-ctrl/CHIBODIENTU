import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import pytz
import io
import time

# ==========================================
# 1. THÔNG SỐ CẤU HÌNH
# ==========================================
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"
# Link dữ liệu thô
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=NhatKyHop"
CONFIG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=CauHinh"

# URL SCRIPT (Đồng chí nhớ kiểm tra kỹ link này trong Apps Script)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxsKDIo8o_rVt_dLGyq5puWNp1XaZLzeBxaesZyQLuMXbqqSkxG9lJXq8gOE4gGy2H-/exec"
ADMIN_NUM = "0927022753"

st.set_page_config(page_title="CHI BỘ ẤP 4", layout="centered", initial_sidebar_state="collapsed")

# ==========================================
# 2. HÀM LẤY DỮ LIỆU (KHÔNG CACHE)
# ==========================================
def get_data_fresh(url):
    try:
        # Tạo mã ngẫu nhiên để ép Google nhả dữ liệu mới nhất
        sep = "&" if "?" in url else "?"
        fresh_url = f"{url}{sep}nocache={int(time.time())}"
        r = requests.get(fresh_url, timeout=10)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.text), dtype=str, encoding='utf-8').fillna("")
        return None
    except:
        return None

# ==========================================
# 3. GIAO DIỆN (CSS)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .header-container {
        background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
        padding: 40px 20px; border-radius: 0 0 35px 35px;
        color: white; text-align: center; margin: -65px -20px 30px -20px;
        box-shadow: 0 10px 20px rgba(211, 47, 47, 0.2);
    }
    .card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .title-red { color: #d32f2f; font-weight: 800; border-left: 5px solid #d32f2f; padding-left: 15px; margin-bottom: 15px; }
    .stButton>button { background: #d32f2f; color: white; border-radius: 12px; font-weight: 700; width: 100%; height: 3.5em; border: none; }
    .info-box { background: #f8f9fa; padding: 12px; border-radius: 10px; border-left: 4px solid #d32f2f; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. LOGIC XÁC THỰC
# ==========================================
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    st.markdown('<div class="header-container"><h1>🇻🇳 CHI BỘ ẤP 4</h1><p>Hệ thống sinh hoạt Đảng điện tử</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("login"):
            sdt = st.text_input("📱 Nhập số điện thoại:", placeholder="09xxxxxxxx")
            if st.form_submit_button("ĐĂNG NHẬP"):
                df_dv = get_data_fresh(CSV_URL)
                if df_dv is not None:
                    target = ''.join(filter(str.isdigit, sdt)).lstrip('0')
                    match = None
                    for _, row in df_dv.iterrows():
                        val_clean = ''.join(filter(str.isdigit, str(row.values))).lstrip('0')
                        if target in val_clean and target != "":
                            match = row.to_dict(); break
                    if match:
                        st.session_state.auth = True
                        st.session_state.user = {"phone": sdt, "data": match}
                        st.rerun()
                    else: st.error("❌ Số điện thoại không đúng.")
                else: st.error("⚠️ Không thể kết nối dữ liệu Sheets.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    is_admin = (''.join(filter(str.isdigit, u['phone'])).lstrip('0') == ''.join(filter(str.isdigit, ADMIN_NUM)).lstrip('0'))
    
    ten_dc = "Đồng chí"
    for v in u['data'].values():
        if v and not str(v).isdigit() and len(str(v)) > 2:
            ten_dc = str(v); break

    st.markdown(f'<div class="header-container"><h2>Chào Đ/c {ten_dc}</h2></div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🇻🇳 CHI BỘ ẤP 4")
        menu = st.radio("Chức năng:", ["🏠 Trang chủ", "👤 Hồ sơ cá nhân", "📊 Quản trị"] if is_admin else ["🏠 Trang chủ", "👤 Hồ sơ cá nhân"])
        if st.button("🚪 Đăng xuất"):
            st.session_state.auth = False; st.rerun()

    # LẤY THÔNG BÁO MỚI NHẤT (ÉP PHÁ CACHE)
    conf_df = get_data_fresh(CONFIG_URL)
    current_meeting = str(conf_df.iloc[0, 0]) if conf_df is not None and not conf_df.empty else "Chưa có nội dung"
    doc_link = str(conf_df.iloc[0, 1]) if conf_df is not None and len(conf_df.columns) > 1 else ""

    # --- TRANG CHỦ ---
    if menu == "🏠 Trang chủ":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">📢 THÔNG BÁO CUỘC HỌP</div>', unsafe_allow_html=True)
        st.info(f"📍 **Nội dung:** {current_meeting}")
        if doc_link and "http" in doc_link:
            st.markdown(f"🔗 [**Xem tài liệu cuộc họp**]({doc_link})")
        
        # Kiểm tra điểm danh
        df_log = get_data_fresh(LOG_URL)
        my_status = None
        if df_log is not None and not df_log.empty:
            target_p = ''.join(filter(str.isdigit, u['phone'])).lstrip('0')
            check = df_log[df_log.iloc[:, 1].str.contains(target_p) & (df_log.iloc[:, 4] == current_meeting)]
            if not check.empty: my_status = check.iloc[0, 3]

        if my_status:
            st.success(f"✅ Đồng chí đã báo: **{my_status}**")
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ CÓ MẶT"):
                    requests.post(SCRIPT_URL, data=json.dumps({"sheetName":"NhatKyHop","values":[datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, "Có mặt", current_meeting, ""]}))
                    st.rerun()
            with c2:
                if st.button("❌ BÁO VẮNG"):
                    st.session_state.absent = True
            if st.session_state.get('absent'):
                lydo = st.text_input("Lý do vắng:")
                if st.button("GỬI BÁO VẮNG"):
                    requests.post(SCRIPT_URL, data=json.dumps({"sheetName":"NhatKyHop","values":[datetime.now().strftime("%H:%M %d/%m/%Y"), u['phone'], ten_dc, "Vắng", current_meeting, lydo]}))
                    st.session_state.absent = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- HỒ SƠ ---
    elif menu == "👤 Hồ sơ cá nhân":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">THÔNG TIN ĐẢNG VIÊN</div>', unsafe_allow_html=True)
        for k, v in u['data'].items():
            if v and "Unnamed" not in str(k):
                st.markdown(f'<div class="info-box"><b>{k}:</b> {v}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- QUẢN TRỊ (CHỈ ADMIN) ---
    elif menu == "📊 Quản trị":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="title-red">⚙️ PHÁT HÀNH THÔNG BÁO</div>', unsafe_allow_html=True)
        new_m = st.text_input("Tên cuộc họp mới:", value=current_meeting)
        new_d = st.text_input("Link tài liệu đính kèm:", value=doc_link)
        if st.button("📢 PHÁT HÀNH NGAY"):
            with st.spinner('Đang truyền lệnh tới Google Sheets...'):
                res = requests.post(SCRIPT_URL, data=json.dumps({"sheetName": "CauHinh", "values": [new_m, new_d], "method": "update_config"}))
                if res.status_code == 200:
                    st.success("✅ ĐÃ CẬP NHẬT! Đảng viên sẽ thấy thông báo mới sau vài giây.")
                    time.sleep(2); st.rerun()
                else: st.error("Lỗi Script. Vui lòng kiểm tra lại SCRIPT_URL.")
        st.markdown('</div>', unsafe_allow_html=True)
