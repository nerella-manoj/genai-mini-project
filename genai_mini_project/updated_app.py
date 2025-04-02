import streamlit as st
from scrap import scrape_website
from pdf import search_supabase, store_in_supabase, extract_text_from_pdf
from llm import get_gemini_response

def set_bg():
    """Sets custom background styling."""
    page_bg_img = '''
    <style>
    .stApp {
        background: #1e1e1e; /* Dark background */
        color: white; /* White text */
    }
    h1, h2, h3, h4, h5, h6 {
        font-size: 24px !important;
        color: white;
    }
    body, p, .stMarkdown {
        font-size: 18px !important;
    }
    .stTextInput>div>div>input {
        font-size: 18px !important;
        background-color: #333;
        color: white;
        border-radius: 8px;
        border: 2px solid #555;
        padding: 12px;
    }
    .stButton>button {
        font-size: 18px !important;
        padding: 12px !important;
        border-radius: 10px;
        background: #4b6cb7;
        color: white;
        border: none;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background: #6a11cb;
        transform: scale(1.07);
    }
    .stSidebar {
        background: #2b2b2b;
        color: white;
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def initialize_session_state():
    """Initializes session state variables separately for Web URL and PDF Upload."""
    if "web_questions" not in st.session_state:
        st.session_state.web_questions = []
    if "web_answers" not in st.session_state:
        st.session_state.web_answers = []
    if "pdf_questions" not in st.session_state:
        st.session_state.pdf_questions = []
    if "pdf_answers" not in st.session_state:
        st.session_state.pdf_answers = []
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "Web URL"

def clear_history(mode):
    """Clears stored questions and answers based on mode."""
    if mode == "Web URL":
        st.session_state.web_questions = []
        st.session_state.web_answers = []
    else:
        st.session_state.pdf_questions = []
        st.session_state.pdf_answers = []
    st.success("Chat history cleared!")

def main():
    st.set_page_config(page_title='J-Scrap', layout='wide')
    set_bg()
    st.title("📚 J-Scrap: AI-Powered Insights from Web & PDFs")
    initialize_session_state()
    
    st.sidebar.header("🧭 Pathfinder")
    option = st.sidebar.radio("Choose an option:", ["Web URL", "PDF Upload"], index=0)

    if option != st.session_state.current_mode:
        st.session_state.current_mode = option

    if option == "Web URL":
        handle_web_url()
    elif option == "PDF Upload":
        handle_pdf_upload()

def handle_web_url():
    """Handles web URL scraping and Q&A with a separate input field."""
    st.subheader("🌐 Enter Web URL")
    url = st.text_input("Paste the website URL here:", key="web_url")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🕵️‍♂️ Scrape Webpage"):
            if url:
                st.success(f"🔄 Scraping started for: {url}")
                scraped_text = scrape_website(url)
                store_in_supabase(scraped_text, url)
            else:
                st.error("❌ Please enter a valid URL.")
    handle_question_answering("Web URL")

def handle_pdf_upload():
    """Handles PDF upload and Q&A with a separate input field."""
    st.subheader("🔄 Upload & Process PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_upload")
    
    if uploaded_file is not None:
        st.success("📄 PDF uploaded successfully!")
        with st.spinner("Processing PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            store_in_supabase(text, uploaded_file.name)
            st.success("PDF text extracted and stored in Supabase!")
    handle_question_answering("PDF Upload")

def handle_question_answering(mode):
    """Handles question answering UI and logic separately for Web URL and PDF Upload."""
    st.subheader("❓ Ask a Question")
    user_question = st.text_input("Your question:", key=f"{mode}_question")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        submit_pressed = st.button("Submit", key=f"{mode}_submit")
    with col2:
        clear_pressed = st.button("🗑️ Clear History", key=f"{mode}_clear")
    
    if submit_pressed:
        if user_question:
            with st.spinner("Searching relevant context..."):
                result = search_supabase(user_question)
                question, contexts = result["question"], result["contexts"]
            
            with st.spinner("Generating answer..."):
                response = get_gemini_response(question, contexts)
            
            if mode == "Web URL":
                st.session_state.web_questions.insert(0, question)
                st.session_state.web_answers.insert(0, response)
            else:
                st.session_state.pdf_questions.insert(0, question)
                st.session_state.pdf_answers.insert(0, response)
            
            st.write(f"🤔 *You asked:* {question}")
            st.write(f"📝 *Answer:* {response}")
        else:
            st.error("❌ Please enter a question.")
    
    if clear_pressed:
        clear_history(mode)
    
    if mode == "Web URL" and st.session_state.web_questions:
        display_history(st.session_state.web_questions, st.session_state.web_answers)
    elif mode == "PDF Upload" and st.session_state.pdf_questions:
        display_history(st.session_state.pdf_questions, st.session_state.pdf_answers)

def display_history(questions, answers):
    """Displays previous questions and answers."""
    st.subheader("📜 Previous Questions")
    for q, a in zip(questions, answers):
        st.write(f"**Q:** {q}")
        st.write(f"**A:** {a}")
        st.write("---")

if __name__ == "__main__":
    main()
