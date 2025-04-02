import streamlit as st
from scrap import scrape_website
from pdf import search_supabase, store_in_supabase, extract_text_from_pdf
from llm import get_gemini_response

def set_bg():
    """Sets custom background styling."""
    page_bg_img = '''
    <style>
    .stApp { background-color: #f4f4f4; }
    .stButton>button {
        width: auto;
        min-width: 150px;
        max-width: 200px;
        border-radius: 10px;
        font-size: 16px;
        padding: 8px;
        background: linear-gradient(to right, #6a11cb, #2575fc);
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button {
            background: linear-gradient(to right, #d3d3d3, #a6a6a6);  /* Soft gradient for light background */
            color: black;  /* Dark text for contrast */
            border-radius: 8px;  /* Rounded corners */
            padding: 8px 16px;
            font-size: 16px;
            border: none;
            transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
         background: linear-gradient(to right, #b3b3b3, #808080);  /* Darker shade on hover */
         color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #2575fc;
        padding: 10px;
        font-size: 16px;
    }
    .css-1d391kg {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

def initialize_session_state():
    """Initializes session state variables."""
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "Web URL"  # Default mode

def clear_history():
    """Clears stored questions and answers."""
    st.session_state.questions = []
    st.session_state.answers = []
    st.success("Chat history cleared!")

def main():
    st.set_page_config(page_title='J-Scrap', layout='wide')
    set_bg()
    st.title("📚 J-Scrap: AI-Powered Insights from Web & PDFs")
    # st.markdown("### Extract, Store, and Query AI for Instant Answers!")
    initialize_session_state()

    st.sidebar.header("🧭 Pathfinder")
    option = st.sidebar.radio("Choose an option:", ["Web URL", "PDF Upload"], index=0)

    if option != st.session_state.current_mode:
        st.session_state.current_mode = option
        # clear_history()
        st.session_state.questions = []
        st.session_state.answers = []

    if option == "Web URL":
        handle_web_url()
    elif option == "PDF Upload":
        handle_pdf_upload()

def handle_web_url():
    """Handles web URL scraping and Q&A."""
    st.subheader("🌐 Enter Web URL")
    url = st.text_input("Paste the website URL here:")
    
    if st.button("🕵️‍♂️ Scrape Webpage"):
        if url:
            st.success(f"🔄 Scraping started for: {url}")
            scraped_text = scrape_website(url)
            store_in_supabase(scraped_text, url)
        else:
            st.error("❌ Please enter a valid URL.")

    handle_question_answering()

def handle_pdf_upload():
    """Handles PDF upload and Q&A."""
    st.subheader("🔄 Upload & Process PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("📄 PDF uploaded successfully!")
        with st.spinner("Processing PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            store_in_supabase(text, uploaded_file.name)
            st.success("PDF text extracted and stored in Supabase!")

    handle_question_answering()

def handle_question_answering():
    """Handles question answering UI and logic."""
    st.subheader("❓ Ask a Question")
    user_question = st.text_input("Your question:")
    
    col1, col2 = st.columns([1, 1])  # Create two columns
    with col1:
        submit_pressed = st.button("Submit")
    with col2:
        clear_pressed = st.button("🗑️ Clear History")
    
    if submit_pressed:
        if user_question:
            with st.spinner("Searching relevant context..."):
                result = search_supabase(user_question)
                question, contexts = result["question"], result["contexts"]
            
            with st.spinner("Generating answer..."):
                response = get_gemini_response(question, contexts)
            
            st.session_state.questions.insert(0, question)
            st.session_state.answers.insert(0, response)
            
            st.write(f"🤔 *You asked:* {question}")
            st.write(f"📝 *Answer:* {response}")
        else:
            st.error("❌ Please enter a question.")
    
    if clear_pressed:
        clear_history()
    
    if st.session_state.questions:
        st.subheader("📜 Previous Questions")
        for q, a in zip(st.session_state.questions, st.session_state.answers):
            st.write(f"**Q:** {q}")
            st.write(f"**A:** {a}")
            st.write("---")

if __name__ == "__main__":
    main()




















































# """code for separate chatbot UI"""

# import streamlit as st
# from scrap import scrape_website
# from pdf import search_supabase, store_in_supabase  # ✅ Import store function from pdf.py
# from llm import get_gemini_response  # ✅ Import LLM function from llm.py

# def set_bg():
#     page_bg_img = '''
#     <style>
#     body {
#         background-color: #f4f4f4;
#     }
#     .stButton>button {
#         width: auto;  /* ✅ Adjust button width */
#         min-width: 150px;
#         max-width: 200px;
#         border-radius: 10px;
#         font-size: 16px;
#         padding: 8px;
#         background: linear-gradient(to right, #6a11cb, #2575fc);
#         color: white;
#         border: none;
#         transition: 0.3s;
#     }
#     .stButton>button:hover {
#         transform: scale(1.05);
#         background: linear-gradient(to right, #2575fc, #6a11cb);
#     }
#     .stTextInput>div>div>input {
#         border-radius: 10px;
#         border: 2px solid #2575fc;
#         padding: 10px;
#         font-size: 16px;
#     }
#     .css-1d391kg {
#         background-color: white;
#         padding: 20px;
#         border-radius: 15px;
#         box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
#     }
#     </style>
#     '''
#     st.markdown(page_bg_img, unsafe_allow_html=True)

# def main():
#     st.set_page_config(page_title='J-Scrap', layout='wide')
#     set_bg()
    
#     st.sidebar.header("🔍 Navigation")
    
#     if "show_chatbot" not in st.session_state:
#         st.session_state.show_chatbot = False

#     if st.session_state.show_chatbot:
#         open_chatbot()
#         return  # ✅ Exit to load chatbot UI only

#     option = st.sidebar.radio("Choose an option:", ["Web URL", "PDF Upload"], index=0)
    
#     if option == "Web URL":
#         st.subheader("🔗 Enter Web URL")
#         url = st.text_input("Paste the website URL here:")
#         if st.button("🚀 Scrape Webpage"):
#             if url:
#                 st.success(f"✅ Scraping started for: {url}")
#                 scraped_text = scrape_website(url)
#                 store_in_supabase(scraped_text, url)  # ✅ Store in Supabase
#                 st.text_area("Extracted Content:", scraped_text, height=300)
#             else:
#                 st.error("❌ Please enter a valid URL.")
            
#     elif option == "PDF Upload":
#         st.subheader("📄 Upload a PDF File")
#         uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
#         if uploaded_file is not None:
#             st.success("✅ PDF uploaded successfully!")
#             from pdf import extract_text_from_pdf
#             with st.spinner("Processing PDF..."):
#                 text = extract_text_from_pdf(uploaded_file)
#                 store_in_supabase(text, uploaded_file.name)
#                 st.success("PDF text extracted and stored in Supabase!")

#     st.sidebar.markdown("---")
#     if st.sidebar.button("💬 Open Chatbot"):
#         st.session_state.show_chatbot = True

# def open_chatbot():
#     """Separate UI for chatbot."""
#     st.title("🤖 Chatbot")
#     st.markdown("Ask me anything!")

#     user_input = st.text_input("Your question:")
    
#     if st.button("Submit"):
#         if user_input:
#             with st.spinner("Searching relevant context..."):
#                 result = search_supabase(user_input)  # ✅ Get relevant contexts
#                 question, contexts = result["question"], result["contexts"]
            
#             with st.spinner("Generating answer..."):
#                 response = get_gemini_response(question, contexts)  # ✅ Pass to LLM
            
#             st.write(f"🤔 *You asked:* {question}")
#             st.write(f"📝 *Answer:* {response}")
#         else:
#             st.error("❌ Please enter a question.")

#     if st.button("⬅️ Back"):
#         st.session_state.show_chatbot = False

# if __name__ == "__main__":
#     main()




# """"code for chatbot UI with history and clear button"""


# import streamlit as st
# from scrap import scrape_website
# from pdf import search_supabase, store_in_supabase, extract_text_from_pdf
# from llm import get_gemini_response

# def set_bg():
#     """Sets custom background styling."""
#     page_bg_img = '''
#     <style>
#     body { background-color: #f4f4f4; }
#     .stButton>button {
#         width: auto;
#         min-width: 150px;
#         max-width: 200px;
#         border-radius: 10px;
#         font-size: 16px;
#         padding: 8px;
#         background: linear-gradient(to right, #6a11cb, #2575fc);
#         color: white;
#         border: none;
#         transition: 0.3s;
#     }
#     .stButton>button:hover {
#         transform: scale(1.05);
#         background: linear-gradient(to right, #2575fc, #6a11cb);
#     }
#     .stTextInput>div>div>input {
#         border-radius: 10px;
#         border: 2px solid #2575fc;
#         padding: 10px;
#         font-size: 16px;
#     }
#     .css-1d391kg {
#         background-color: white;
#         padding: 20px;
#         border-radius: 15px;
#         box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
#     }
#     </style>
#     '''
#     st.markdown(page_bg_img, unsafe_allow_html=True)

# def initialize_session_state():
#     """Initializes session state variables."""
#     if "questions" not in st.session_state:
#         st.session_state.questions = []
#     if "answers" not in st.session_state:
#         st.session_state.answers = []
#     if "current_mode" not in st.session_state:
#         st.session_state.current_mode = "Web URL"  # Default mode

# def clear_history():
#     """Clears stored questions and answers."""
#     st.session_state.questions = []
#     st.session_state.answers = []
#     st.success("Chat history cleared!")

# def main():
#     st.set_page_config(page_title='J-Scrap', layout='wide')
#     set_bg()
#     initialize_session_state()

#     st.sidebar.header("🔍 Navigation")

#     # Handle mode switching to clear history when changing options
#     option = st.sidebar.radio("Choose an option:", ["Web URL", "PDF Upload"], index=0)

#     if option != st.session_state.current_mode:
#         st.session_state.current_mode = option
#         clear_history()

#     if option == "Web URL":
#         handle_web_url()
#     elif option == "PDF Upload":
#         handle_pdf_upload()

# def handle_web_url():
#     """Handles web URL scraping and Q&A."""
#     st.subheader("🔗 Enter Web URL")
#     url = st.text_input("Paste the website URL here:")
    
#     if st.button("🚀 Scrape Webpage"):
#         if url:
#             st.success(f"✅ Scraping started for: {url}")
#             scraped_text = scrape_website(url)
#             store_in_supabase(scraped_text, url)
#             # st.text_area("Extracted Content:", scraped_text, height=300)
#         else:
#             st.error("❌ Please enter a valid URL.")

#     handle_question_answering()

# def handle_pdf_upload():
#     """Handles PDF upload and Q&A."""
#     st.subheader("📄 Upload a PDF File")
#     uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
#     if uploaded_file is not None:
#         st.success("✅ PDF uploaded successfully!")
#         with st.spinner("Processing PDF..."):
#             text = extract_text_from_pdf(uploaded_file)
#             store_in_supabase(text, uploaded_file.name)
#             st.success("PDF text extracted and stored in Supabase!")

#     handle_question_answering()

# def handle_question_answering():
#     """Handles question answering UI and logic."""
#     st.subheader("💬 Ask a Question")
#     user_question = st.text_input("Your question:")

#     if st.button("Submit"):
#         if user_question:
#             with st.spinner("Searching relevant context..."):
#                 result = search_supabase(user_question)
#                 question, contexts = result["question"], result["contexts"]

#             with st.spinner("Generating answer..."):
#                 response = get_gemini_response(question, contexts)

#             # Store in session state for history
#             st.session_state.questions.insert(0, question)  # Latest on top
#             st.session_state.answers.insert(0, response)

#             st.write(f"🤔 *You asked:* {question}")
#             st.write(f"📝 *Answer:* {response}")
#         else:
#             st.error("❌ Please enter a question.")

#     # Display question-answer history
#     if st.session_state.questions:
#         st.subheader("📜 Previous Questions")
#         for q, a in zip(st.session_state.questions, st.session_state.answers):
#             st.write(f"**Q:** {q}")
#             st.write(f"**A:** {a}")
#             st.write("---")

#     # Clear history button
#     if st.button("🗑️ Clear History"):
#         clear_history()

# if __name__ == "__main__":
#     main()






