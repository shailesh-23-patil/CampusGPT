from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import numpy as np
import faiss
from pypdf import PdfReader
from google import genai
from google.genai import types
import uuid

# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
app.secret_key = 'replace-with-strong-secret-key'



# =========================================================
# GEMINI MODELS
# =========================================================

EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-3.5-flash-lite"


# =========================================================
# GLOBAL VARIABLES
# =========================================================

# In-memory storage for each user session
USER_DATA = {}

# Helper to retrieve or create per‑session data
def get_user_data():
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    if session_id not in USER_DATA:
        USER_DATA[session_id] = {
            'client': None,
            'all_chunks': [],
            'faiss_index': None,
            'processed_files': [],
            'chat_history': []
        }
    return USER_DATA[session_id]


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    page_background_path = Path(app.static_folder) / "campus-code-scene.jpg"
    return render_template(
        "index.html",
        page_background_available=page_background_path.is_file()
    )


# =========================================================
# SET GEMINI API KEY
# =========================================================

@app.route("/set-api-key", methods=["POST"])
def set_api_key():

    ud = get_user_data()

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request."}), 400

    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"error": "Please enter your Gemini API key."}), 400

    try:
        client = genai.Client(api_key=api_key)
        ud['client'] = client
        session['api_key'] = api_key
        return jsonify({"success": True, "message": "Gemini connected successfully."})
    except Exception as e:
        ud['client'] = None
        return jsonify({"error": str(e)}), 500


# =========================================================
# LOAD PDF
# =========================================================

def load_pdf(uploaded_file):

    filename = getattr(uploaded_file, "filename", None) or Path(uploaded_file).name

    try:
        reader = PdfReader(uploaded_file)
    except Exception as e:
        raise ValueError(f"Failed to read PDF '{filename}': {str(e)}")

    pages_data = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        if text.strip():

            pages_data.append({

                "source":
                    filename,

                "page":
                    page_number,

                "text":
                    text

            })

    return pages_data


# =========================================================
# TEXT CHUNKING
# =========================================================

def chunk_pages(
    pages_data,
    chunk_size=150,
    overlap=30
):

    chunks = []

    for page_data in pages_data:

        words = page_data["text"].split()

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk_text = " ".join(
                words[start:end]
            )

            if chunk_text.strip():

                chunks.append({

                    "id":
                        len(chunks),

                    "text":
                        chunk_text,

                    "source":
                        page_data["source"],

                    "page":
                        page_data["page"]

                })

            start += chunk_size - overlap

    return chunks


# =========================================================
# CREATE DOCUMENT EMBEDDINGS
# =========================================================

def create_document_embeddings(chunks):

    ud = get_user_data()
    client = ud['client']

    embeddings = []

    for chunk in chunks:

        result = client.models.embed_content(

            model=EMBEDDING_MODEL,

            contents=chunk["text"],

            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )

        )

        embeddings.append(
            result.embeddings[0].values
        )

    return embeddings


# =========================================================
# CREATE FAISS INDEX
# =========================================================

def create_faiss_index(embeddings):

    embedding_matrix = np.array(
        embeddings,
        dtype="float32"
    )

    faiss.normalize_L2(
        embedding_matrix
    )

    dimension = embedding_matrix.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embedding_matrix
    )

    return index


# =========================================================
# CREATE QUESTION EMBEDDING
# =========================================================

def create_question_embedding(question):

    ud = get_user_data()
    client = ud['client']

    result = client.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=question,

        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )

    )

    question_embedding = np.array(
        [
            result.embeddings[0].values
        ],
        dtype="float32"
    )

    faiss.normalize_L2(
        question_embedding
    )

    return question_embedding


# =========================================================
# CHAT HISTORY
# =========================================================

def get_chat_history_text():
    ud = get_user_data()
    chat_history = ud['chat_history']
    if not chat_history:
        return "No previous conversation."
    history_text = ""
    for message in chat_history[-6:]:
        role = message["role"].title()
        content = message["content"]
        history_text += f"{role}: {content}\n"
    return history_text


# =========================================================
# CONTEXT-AWARE SEARCH
# =========================================================

def create_search_question(question):

    ud = get_user_data()
    chat_history = ud['chat_history']

    if not chat_history:

        return question

    return f"""
Previous conversation:

{get_chat_history_text()}

Current question:

{question}
"""


# =========================================================
# GENERATE AI ANSWER
# =========================================================

def generate_answer(prompt):

    ud = get_user_data()
    client = ud['client']

    try:

        response = client.models.generate_content(

            model=GENERATION_MODEL,

            contents=prompt

        )

        return response.text

    except Exception as e:

        error_message = str(e)

        if (
            "429" in error_message
            or
            "RESOURCE_EXHAUSTED"
            in error_message
        ):

            return (
                "Gemini API quota has been "
                "exceeded. Please try again "
                "after the quota resets."
            )

        if (
            "503" in error_message
            or
            "UNAVAILABLE"
            in error_message
        ):

            return (
                "Gemini is temporarily "
                "unavailable. Please try "
                "again in a few moments."
            )

        return (
            "Gemini API error: "
            + error_message
        )


# =========================================================
# ASK CAMPUSGPT
# =========================================================

def ask_question(question, k=3):

    ud = get_user_data()
    faiss_index = ud['faiss_index']
    all_chunks = ud['all_chunks']

    if faiss_index is None:

        return (
            "Please process your study "
            "material first.",
            []
        )

    if faiss_index.ntotal == 0:

        return (
            "No document data is available.",
            []
        )

    k = min(
        k,
        faiss_index.ntotal
    )

    similarity_threshold = 0.50

    search_question = (
        create_search_question(question)
    )

    question_embedding = (
        create_question_embedding(
            search_question
        )
    )

    scores, indices = faiss_index.search(
        question_embedding,
        k
    )

    retrieved_context = ""

    sources = []

    for i in range(k):

        chunk_index = int(
            indices[0][i]
        )

        if (
            chunk_index < 0
            or
            chunk_index >= len(all_chunks)
        ):

            continue

        chunk = all_chunks[
            chunk_index
        ]

        score = float(
            scores[0][i]
        )

        if score < similarity_threshold:

            continue

        retrieved_context += (
            f"[Source: {chunk['source']}, "
            f"Page: {chunk['page']}]\n"
            f"{chunk['text']}\n\n"
        )

        sources.append({

            "source":
                chunk["source"],

            "page":
                chunk["page"],

            "score":
                score

        })

    if not retrieved_context:

        return (
            "I couldn't find that information "
            "in the uploaded PDF(s).",
            sources
        )

    prompt = f"""
You are CampusGPT, an AI learning assistant for students.

Your task is to answer the student's question using ONLY
the information provided in the retrieved context.

You may use the recent conversation to understand
follow-up questions and references such as:

"it"
"this"
"that"
"the first one"
"the second one"

However, the actual answer must come ONLY from
the retrieved PDF context.

Do NOT use outside knowledge.

If the answer is not present in the retrieved context,
reply exactly:

"I couldn't find that information in the uploaded PDF(s)."

For facts taken from the context, cite the source and page
using this format:

(Source: file.pdf, Page: 3)

Recent Conversation:

{get_chat_history_text()}

Retrieved Context:

{retrieved_context}

Student Question:

{question}

Answer clearly and in simple language.
"""

    answer = generate_answer(prompt)

    return answer, sources


# =========================================================
# PROCESS PDF
# =========================================================

@app.route("/process", methods=["POST"])
def process_documents():

    ud = get_user_data()

    if ud['client'] is None:
        return jsonify({"error": "Please enter your Gemini API key first."}), 400

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "Please upload at least one PDF."}), 400

    try:
        pages_data = []
        ud['processed_files'] = []

        for uploaded_file in files:
            if not uploaded_file.filename:
                continue
            if not uploaded_file.filename.lower().endswith('.pdf'):
                continue
            pages_data.extend(load_pdf(uploaded_file))
            ud['processed_files'].append(uploaded_file.filename)

        if not pages_data:
            return jsonify({"error": "No readable text was found in the uploaded PDF(s)."}), 400

        ud['all_chunks'] = chunk_pages(pages_data, chunk_size=150, overlap=30)
        if not ud['all_chunks']:
            return jsonify({"error": "No text chunks were created."}), 400

        embeddings = create_document_embeddings(ud['all_chunks'])
        ud['faiss_index'] = create_faiss_index(embeddings)
        ud['chat_history'] = []

        return jsonify({
            "success": True,
            "documents": len(ud['processed_files']),
            "chunks": len(ud['all_chunks']),
            "files": ud['processed_files'],
            "message": "Study material processed successfully."
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# ASK ROUTE
# =========================================================

@app.route("/ask", methods=["POST"])
def ask():

    ud = get_user_data()

    if ud['client'] is None:
        return jsonify({"error": "Please enter your Gemini API key first."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request."}), 400

    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        answer, sources = ask_question(question, k=3)
        ud['chat_history'].append({"role": "user", "content": question})
        ud['chat_history'].append({"role": "assistant", "content": answer})
        return jsonify({"success": True, "answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# TEST GEMINI
# =========================================================

@app.route("/test-gemini", methods=["GET"])
def test_gemini():

    ud = get_user_data()
    client = ud['client']

    if client is None:
        return jsonify({"error": "Gemini API key is not configured."}), 400

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents="Say hello in one sentence."
        )

        return jsonify({
            "success": True,
            "message": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )