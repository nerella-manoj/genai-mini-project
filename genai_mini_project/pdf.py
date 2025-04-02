# import fitz  # PyMuPDF for PDF processing
# import hashlib
# import json
# import os
# import time
# from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer
# from supabase import create_client, Client

# # Load environment variables
# load_dotenv()

# # Retrieve Supabase credentials from .env
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# # Create Supabase client
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Embedding Model
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# def extract_text_from_pdf(pdf_file):
#     """Extracts text from an uploaded PDF file."""
#     doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
#     text = "\n".join([page.get_text("text") for page in doc])
#     return text

# def store_in_supabase(text, filename):
#     """Deletes old data in batches and stores new text with embeddings in Supabase."""
#     # ✅ Delete old records in batches to prevent overload
#     while True:
#         response = supabase.table("documents").select("doc_id").limit(100).execute()
#         if not response.data:
#             break  # Stop when no more data
#         supabase.table("documents").delete().in_("doc_id", [item["doc_id"] for item in response.data]).execute()
#         time.sleep(1)  # Prevent Supabase rate limit errors

#     # ✅ Store new document embeddings
#     doc_id = hashlib.md5(filename.encode()).hexdigest()
#     chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]  # 🔹 Increased chunk size to 1000 chars
#     embeddings = embed_model.encode(chunks).tolist()

#     batch_size = 10  # Insert in batches to prevent API overload
#     batch_data = []

#     for chunk, embedding in zip(chunks, embeddings):
#         batch_data.append({"doc_id": doc_id, "text": chunk, "embedding": json.dumps(embedding)})
        
#         if len(batch_data) >= batch_size:
#             supabase.table("documents").insert(batch_data).execute()
#             batch_data = []  # Reset batch
#             time.sleep(1)  # Prevent rate limiting

#     if batch_data:  # Insert remaining data
#         supabase.table("documents").insert(batch_data).execute()

# def search_supabase(query, top_k=20):
#     """Searches Supabase for relevant embeddings and retrieves top 20 matching contexts."""
#     query_embedding = embed_model.encode([query]).tolist()[0]

#     try:
#         response = supabase.rpc(
#             "match_documents",
#             {"query_embedding": query_embedding, "match_count": top_k}
#         ).execute()

#         if response.data:
#             # 🔹 Merge multiple retrieved contexts into a single long context
#             contexts = " ".join([item["text"] for item in response.data])
#             return {"question": query, "contexts": [contexts]}
        
#     except Exception as e:
#         print("Supabase Search Error:", str(e))  # Debugging
#         return {"question": query, "contexts": ["Error retrieving results."]}

#     return {"question": query, "contexts": ["No relevant information found."]}






import fitz  # PyMuPDF for PDF processing
import hashlib
import json
import os
import time
import httpx
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Retrieve Supabase credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Embedding Model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def delete_old_data():
    """Deletes old records in batches to prevent overload."""
    while True:
        try:
            response = supabase.table("documents").select("doc_id").limit(100).execute()
            if not response.data:
                break  # Stop when no more data
            
            doc_ids = [item["doc_id"] for item in response.data]
            supabase.table("documents").delete().in_("doc_id", doc_ids).execute()
            time.sleep(2)  # Prevent Supabase rate limit errors
        except httpx.RemoteProtocolError:
            print("🔄 Server disconnected, retrying delete operation...")
            time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"❌ Error deleting old data: {e}")
            break

def store_in_supabase(text, filename, max_retries=3):
    """Stores new text with embeddings in Supabase after deleting old records."""
    delete_old_data()  # ✅ Delete old records first

    doc_id = hashlib.md5(filename.encode()).hexdigest()
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]  # 🔹 Chunk size: 1000 chars
    embeddings = embed_model.encode(chunks).tolist()

    batch_size = 10  # Insert in batches to prevent API overload
    batch_data = []

    for chunk, embedding in zip(chunks, embeddings):
        batch_data.append({"doc_id": doc_id, "text": chunk, "embedding": json.dumps(embedding)})

        if len(batch_data) >= batch_size:
            insert_with_retries(batch_data, max_retries)
            batch_data = []  # Reset batch

    if batch_data:  # Insert remaining data
        insert_with_retries(batch_data, max_retries)

def insert_with_retries(batch_data, max_retries=3):
    """Inserts data into Supabase with retry handling."""
    for attempt in range(max_retries):
        try:
            supabase.table("documents").insert(batch_data).execute()
            time.sleep(2)  # Prevent API rate limit errors
            return
        except httpx.RemoteProtocolError:
            print(f"🔄 Server disconnected, retrying insert... ({attempt + 1}/{max_retries})")
            time.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"❌ Error inserting data: {e}")
            break  # Stop retrying if another error occurs

def search_supabase(query, top_k=20):
    """Searches Supabase for relevant embeddings and retrieves top results."""
    query_embedding = embed_model.encode([query]).tolist()[0]

    try:
        response = supabase.rpc(
            "match_documents",
            {"query_embedding": query_embedding, "match_count": top_k}
        ).execute()

        if response.data:
            contexts = " ".join([item["text"] for item in response.data])
            return {"question": query, "contexts": [contexts]}
        
    except httpx.RemoteProtocolError:
        print("🔄 Server disconnected during search, retrying...")
        time.sleep(5)
        return search_supabase(query, top_k)  # Retry search once

    except Exception as e:
        print(f"❌ Supabase Search Error: {e}")
        return {"question": query, "contexts": ["Error retrieving results."]}

    return {"question": query, "contexts": ["No relevant information found."]}
