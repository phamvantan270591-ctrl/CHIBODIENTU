import streamlit as st
import pandas as pd
import requests
import json
import time

# ID CHUẨN CỦA ĐỒNG CHÍ
SHEET_ID = "1WKGPX3adetYHr7Z-yIegxADiRkrw8KWf5WZ6dQeIxPM"

# Hàm lấy link CSV đảm bảo không bị chặn
def get_raw_url(gid_id=0):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid_id}&t={int(time.time())}"

st.set_page_config(page_title="HỆ THỐNG CHI BỘ", layout="centered")

# --- THỬ KẾT NỐI ---
st.markdown("<h2 style='text-align: center; color: #d32f2f;'>🇻🇳 KIỂM TRA KẾT NỐI</h2>", unsafe_allow_html=True)

try:
    # Thử đọc dữ liệu trực tiếp
    test_df = pd.read_csv(get_raw_url(), dtype=str)
    
    st.success("✅ KẾT NỐI THÀNH CÔNG!")
    st.write(f"Tìm thấy **{len(test_df)}** dòng dữ liệu trong danh sách Đảng viên.")
    
    # Nếu kết nối ok, hiện nút để vào ứng dụng
    if st.button("TIẾP TỤC VÀO HỆ THỐNG"):
        st.info("Đồng chí hãy dùng bản code đầy đủ tôi đã gửi ở tin nhắn trước để chạy chính thức nhé!")

except Exception as e:
    st.error("❌ VẪN CHƯA KẾT NỐI ĐƯỢC")
    st.warning("Lý do có thể là:")
    st.write("- Đồng chí chưa nhấn 'Bất kỳ ai có đường liên kết' trong mục Chia sẻ.")
    st.write("- ID Sheet trong code bị sai.")
    st.write(f"**Lỗi kỹ thuật:** {e}")
    
    # Hiển thị hướng dẫn hình ảnh giả lập
    st.info("Đồng chí hãy chụp ảnh màn hình mục 'Chia sẻ' trong Sheets gửi cho tôi nếu vẫn lỗi nhé!")
