import streamlit as st
import google.generativeai as genai
import json
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="AI Python Quiz Generator", layout="wide")

st.title("🤖 HUST Python Quiz Master")
st.markdown("Nhập chủ đề Python bạn muốn ôn, AI sẽ tạo đề thi ngay lập tức.")

# --- SIDEBAR: CẤU HÌNH API ---
with st.sidebar:
    st.header("Cấu hình")
    # Bạn có thể lấy key miễn phí tại: https://aistudio.google.com/app/apikey
    api_key = st.text_input("Nhập Google Gemini API Key", type="password")
    if not api_key:
        st.warning("Vui lòng nhập API Key để bắt đầu.")
        st.stop()
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

# --- HÀM GỌI AI ĐỂ TẠO QUIZ ---
def generate_quiz(topic, num_questions=5):
    prompt = f"""
    Bạn là giảng viên dạy lập trình Python tại đại học Bách Khoa.
    Hãy tạo {num_questions} câu hỏi trắc nghiệm về chủ đề: "{topic}".
    Độ khó: Tương đương đề thi cuối kỳ môn Nhập môn lập trình.
    
    YÊU CẦU OUTPUT: Trả về CHỈ MỘT chuỗi JSON (không markdown, không code block) theo định dạng sau:
    [
        {{
            "question": "Nội dung câu hỏi",
            "code_snippet": "Đoạn code minh họa (nếu có, nếu không thì để null)",
            "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
            "correct_answer_index": 0,
            "explanation": "Giải thích chi tiết tại sao đúng/sai"
        }},
        ...
    ]
    Lưu ý: correct_answer_index là số nguyên từ 0 đến 3 tương ứng với vị trí trong mảng options.
    """
    
    try:
        response = model.generate_content(prompt)
        # Xử lý text để đảm bảo format JSON chuẩn
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        return json.loads(text_response)
    except Exception as e:
        st.error(f"Lỗi khi tạo câu hỏi: {e}")
        return []

# --- QUẢN LÝ STATE (LƯU TRẠNG THÁI) ---
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# --- GIAO DIỆN CHÍNH ---

# 1. Input người dùng
col1, col2 = st.columns([3, 1])
with col1:
    topic_input = st.text_input("Chủ đề ôn tập (VD: List slicing, Recursion, OOP...)", "Python List Slicing")
with col2:
    num_q = st.number_input("Số câu", min_value=1, max_value=10, value=3)

if st.button("🚀 Tạo đề thi mới", use_container_width=True):
    with st.spinner("AI đang soạn đề... vui lòng đợi chút..."):
        st.session_state.quiz_data = generate_quiz(topic_input, num_q)
        st.session_state.user_answers = {} # Reset câu trả lời cũ

# 2. Hiển thị câu hỏi
if st.session_state.quiz_data:
    st.divider()
    score = 0
    total = len(st.session_state.quiz_data)

    for i, q in enumerate(st.session_state.quiz_data):
        st.subheader(f"Câu {i+1}: {q['question']}")
        
        # Hiển thị code snippet nếu có
        if q.get('code_snippet'):
            st.code(q['code_snippet'], language='python')
        
        # Tạo key độc nhất cho mỗi widget
        radio_key = f"q_{i}"
        
        # Lấy đáp án đã chọn (nếu có)
        user_choice = st.radio(
            "Chọn đáp án:", 
            q['options'], 
            index=None, 
            key=radio_key
        )
        
        # Nút kiểm tra cho từng câu
        if user_choice:
            chosen_index = q['options'].index(user_choice)
            correct_index = q['correct_answer_index']
            
            if st.button(f"Kiểm tra câu {i+1}", key=f"btn_{i}"):
                if chosen_index == correct_index:
                    st.success("✅ Chính xác!")
                else:
                    st.error(f"❌ Sai rồi. Đáp án đúng là: {q['options'][correct_index]}")
                
                with st.expander("📖 Xem giải thích chi tiết"):
                    st.markdown(q['explanation'])
            
        st.divider()

else:

    st.info("Hãy nhập chủ đề và nhấn nút 'Tạo đề thi mới' để bắt đầu.")
