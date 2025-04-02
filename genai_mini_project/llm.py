import os
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load API key from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(context, question):
    """Gets response from Gemini AI based strictly on retrieved context."""
    
    # ✅ Ensure there is context; otherwise, return no data
    if not context.strip():
        return "No Relevant Data Found."

    model = genai.GenerativeModel("gemini-1.5-pro")
    
    prompt = f"""
    You are an AI assistant answering questions based on a document.

    Context:
    {context}

    Question:
    {question}

    Answer strictly based on the provided context.
    Do NOT generate generic responses beyond the given data.
    If no relevant information is found, reply: "No Relevant Data Found."
    Keep responses concise and relevant.
    """

    response = model.generate_content(prompt)
    
    return response.text.strip() if response else "No Relevant Data Found."
