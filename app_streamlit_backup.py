import streamlit as st
import numpy as np
import faiss
from pypdf import PdfReader
from google import genai
from google.genai import types
import time


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="CampusGPT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# CUSTOM UI
# =====================================================

st.markdown(
    """
<style>
/* ---------- APP ---------- */
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(99,102,241,.10), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(14,165,233,.09), transparent 25%),
        #f7f9fc;
}
.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 5rem;
}

/* ---------- HERO ---------- */
.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #111827 0%, #312e81 52%, #0f766e 120%);
    border-radius: 28px;
    padding: 38px 40px;
    margin-bottom: 26px;
    box-shadow: 0 18px 50px rgba(30,41,59,.18);
    color: white;
}
.hero:before, .hero:after {
    content: "";
    position: absolute;
    border-radius: 999px;
    background: rgba(255,255,255,.08);
}
.hero:before { width: 230px; height: 230px; right: -80px; top: -100px; }
.hero:after { width: 150px; height: 150px; right: 160px; bottom: -100px; }
.hero-content { position: relative; z-index: 2; }
.hero-icon {
    width: 58px; height: 58px; display: flex; align-items: center; justify-content: center;
    border-radius: 17px; background: rgba(255,255,255,.13);
    font-size: 29px; margin-bottom: 16px;
}
.hero h1 {
    font-size: 46px; line-height: 1.05; font-weight: 850;
    color: #fff; margin: 0;
}
.hero-subtitle {
    font-size: 19px; font-weight: 650; color: rgba(255,255,255,.92);
    margin: 10px 0 7px;
}
.hero-description {
    max-width: 720px; font-size: 15px; line-height: 1.65;
    color: rgba(255,255,255,.72); margin: 0;
}
.hero-badges { display: flex; gap: 9px; flex-wrap: wrap; margin-top: 21px; }
.hero-badge {
    padding: 7px 12px; border-radius: 999px;
    background: rgba(255,255,255,.11); border: 1px solid rgba(255,255,255,.14);
    color: rgba(255,255,255,.9); font-size: 12px; font-weight: 700;
}

/* ---------- SECTION ---------- */
.section-title {
    font-size: 22px; font-weight: 800; color: #172033;
    margin-top: 16px; margin-bottom: 6px;
}
.section-hint { color: #64748b; font-size: 14px; margin-bottom: 15px; }

/* ---------- CARDS ---------- */
.info-card {
    background: rgba(255,255,255,.88); border: 1px solid #e2e8f0;
    border-radius: 18px; padding: 18px 20px; margin-bottom: 14px;
    box-shadow: 0 7px 24px rgba(15,23,42,.045);
}
.file-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 12px 15px; margin: 7px 0; font-weight: 650;
    transition: .2s ease; box-shadow: 0 4px 12px rgba(15,23,42,.03);
}
.file-card:hover { transform: translateY(-2px); border-color: #a5b4fc; }

/* ---------- METRICS ---------- */
.metric-card {
    background: rgba(255,255,255,.92); border: 1px solid #e2e8f0;
    border-radius: 17px; padding: 16px 17px; min-height: 92px;
    box-shadow: 0 6px 20px rgba(15,23,42,.04);
}
.metric-icon { font-size: 20px; }
.metric-value { font-size: 23px; font-weight: 820; color: #172033; margin-top: 4px; }
.metric-label { font-size: 12px; color: #64748b; font-weight: 650; }

/* ---------- QUICK QUESTIONS ---------- */
.quick-card {
    background: linear-gradient(135deg,#ffffff,#f8faff);
    border: 1px solid #e2e8f0; border-radius: 17px; padding: 17px 18px;
    box-shadow: 0 5px 18px rgba(15,23,42,.04);
}
.quick-title { font-size: 15px; font-weight: 800; color: #172033; }
.quick-sub { font-size: 12px; color: #64748b; margin-top: 3px; }

/* ---------- STATUS ---------- */
.status-card {
    background: linear-gradient(135deg,#ecfdf5,#f0fdf4);
    border: 1px solid #bbf7d0; border-radius: 15px;
    padding: 13px 16px; color: #166534; font-weight: 700; margin: 18px 0;
}

/* ---------- CHAT ---------- */
[data-testid="stChatMessage"] {
    border-radius: 18px; margin-bottom: 10px;
}
[data-testid="stChatMessageContent"] {
    font-size: 15px; line-height: 1.7;
}
[data-testid="stChatInput"] { border-radius: 17px; }

/* ---------- SOURCES ---------- */
.source-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 11px 14px; margin: 7px 0; font-size: 13px;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    border-radius: 12px; font-weight: 750; min-height: 43px;
    transition: .18s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(79,70,229,.13);
}
.stTextInput input { border-radius: 12px; }

/* ---------- UPLOADER ---------- */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,.88); border: 1px dashed #94a3b8;
    border-radius: 18px; padding: 10px;
}
[data-testid="stFileUploaderDropzone"] {
    border-radius: 15px;
}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] { border-right: 1px solid #e2e8f0; }
.sidebar-brand { font-size: 23px; font-weight: 850; color: #172033; }
.sidebar-caption { color: #64748b; font-size: 13px; }

/* ---------- FOOTER ---------- */
.footer {
    text-align: center; color: #94a3b8; font-size: 13px;
    margin-top: 44px; padding-top: 20px; border-top: 1px solid #e2e8f0;
}

/* ---------- MOBILE ---------- */
@media (max-width: 700px) {
    .hero { padding: 28px 23px; border-radius: 22px; }
    .hero h1 { font-size: 37px; }
    .hero-subtitle { font-size: 16px; }
}
</style>
""",
    unsafe_allow_html=True
)


# =====================================================
# GEMINI CONFIGURATION
# =====================================================

EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "gemini-3.8-flash"


# =====================================================
# SESSION STATE
# =====================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">🎓 CampusGPT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-caption">Student Learning Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Only one API key input
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        help="Your API key is used only for this session."
    )

    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = None

    st.markdown("---")
    st.markdown("### ⚙️ Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧪 Gemini Connection")

    if client is not None:

        if st.button("Test Gemini", use_container_width=True):

            with st.spinner("Testing Gemini..."):

                try:
                    test_response = client.models.generate_content(
                        model=GENERATION_MODEL,
                        contents="Say hello in one sentence."
                    )

                    st.success(test_response.text)

                except Exception as e:
                    st.error(f"Gemini test failed: {e}")

    else:
        st.info("Enter your Gemini API key above.")

    st.markdown("---")
    st.markdown("### 📌 Project")

    st.caption("RAG-based academic document assistant")
    st.caption("FAISS • Gemini Embeddings • Gemini Flash")


# =====================================================
# PDF LOADING
# =====================================================

def load_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)
    pages_data = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():

            pages_data.append({
                "source": uploaded_file.name,
                "page": page_number,
                "text": text
            })

    return pages_data


# =====================================================
# TEXT CHUNKING
# =====================================================

def chunk_pages(pages_data, chunk_size=150, overlap=30):

    chunks = []

    for page_data in pages_data:

        words = page_data["text"].split()
        start = 0

        while start < len(words):

            end = start + chunk_size
            chunk_text = " ".join(words[start:end])

            if chunk_text.strip():

                chunks.append({
                    "id": len(chunks),
                    "text": chunk_text,
                    "source": page_data["source"],
                    "page": page_data["page"]
                })

            start += chunk_size - overlap

    return chunks


# =====================================================
# DOCUMENT EMBEDDINGS
# =====================================================

def create_document_embeddings(chunks):

    embeddings = []

    for chunk in chunks:

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunk["text"],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )

        embeddings.append(result.embeddings[0].values)

    return embeddings


# =====================================================
# FAISS INDEX
# =====================================================

def create_faiss_index(embeddings):

    embedding_matrix = np.array(
        embeddings,
        dtype="float32"
    )

    faiss.normalize_L2(embedding_matrix)

    dimension = embedding_matrix.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embedding_matrix)

    return index


# =====================================================
# QUESTION EMBEDDING
# =====================================================

def create_question_embedding(question):

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )

    question_embedding = np.array(
        [result.embeddings[0].values],
        dtype="float32"
    )

    faiss.normalize_L2(question_embedding)

    return question_embedding


# =====================================================
# GENERATE AI ANSWER
# =====================================================

def generate_answer(prompt):

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt
            )

            return response.text

        except Exception as e:

            error_message = str(e)

            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue

                return (
                    "Gemini is temporarily unavailable. "
                    "Please try again in a few moments."
                )

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
            ):

                return (
                    "Gemini API quota has been exceeded. "
                    "Please try again after the quota resets."
                )

            return f"Gemini API error: {error_message}"

    return "Gemini was unable to generate an answer."


# =====================================================
# CHAT HISTORY TEXT
# =====================================================

def get_chat_history_text():

    if not st.session_state.chat_history:
        return "No previous conversation."

    history_text = ""

    for message in st.session_state.chat_history[-6:]:

        role = message["role"].title()
        content = message["content"]

        history_text += f"{role}: {content}\n"

    return history_text


# =====================================================
# CONTEXT-AWARE SEARCH
# =====================================================

def create_search_question(question):

    if not st.session_state.chat_history:
        return question

    return f"""
Previous conversation:
{get_chat_history_text()}

Current question:
{question}
"""


# =====================================================
# CAMPUSGPT RAG
# =====================================================

def ask_question(question, chunks, index, k=3):

    if index.ntotal == 0:
        return "No document data is available.", []

    k = min(k, index.ntotal)
    similarity_threshold = 0.50

    search_question = create_search_question(question)

    question_embedding = create_question_embedding(
        search_question
    )

    scores, indices = index.search(
        question_embedding,
        k
    )

    retrieved_context = ""
    sources = []

    for i in range(k):

        chunk_index = int(indices[0][i])

        if (
            chunk_index < 0
            or chunk_index >= len(chunks)
        ):
            continue

        chunk = chunks[chunk_index]
        score = float(scores[0][i])

        if score < similarity_threshold:
            continue

        retrieved_context += (
            f"[Source: {chunk['source']}, "
            f"Page: {chunk['page']}]\n"
            f"{chunk['text']}\n\n"
        )

        sources.append({
            "source": chunk["source"],
            "page": chunk["page"],
            "score": score
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


# =====================================================
# MAIN HEADER
# =====================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-content">'
    '<div class="hero-icon">🎓</div>'
    '<h1>CampusGPT</h1>'
    '<div class="hero-subtitle">Your AI-Powered Student Learning Assistant</div>'
    '<p class="hero-description">'
    'Upload your study material, ask questions, and learn directly '
    'from your own documents using Retrieval-Augmented Generation.'
    '</p>'
    '<div class="hero-badges">'
    '<span class="hero-badge">📚 RAG Powered</span>'
    '<span class="hero-badge">🧠 AI Assisted</span>'
    '<span class="hero-badge">🔎 Source Based</span>'
    '<span class="hero-badge">🎓 Student Focused</span>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# STUDY MATERIAL
# =====================================================

st.markdown(
    '<div class="section-title">📚 Study Material</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-hint">'
    'Upload one or more PDF study materials, '
    'then process them before asking questions.'
    '</div>',
    unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Upload your study PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)


# =====================================================
# SELECTED PDF LIST
# =====================================================

if uploaded_files:

    st.markdown(
        f'<div class="info-card">'
        f'<b>📄 {len(uploaded_files)} PDF(s) selected</b>'
        f'</div>',
        unsafe_allow_html=True
    )

    for file in uploaded_files:

        st.markdown(
            f'<div class="file-card">📄 {file.name}</div>',
            unsafe_allow_html=True
        )


# =====================================================
# PROCESS PDF
# =====================================================

if uploaded_files:

    if client is None:

        st.warning(
            "Please enter your Gemini API key in the sidebar first."
        )

    else:

        if st.button(
            "⚡ Process Study Material",
            use_container_width=True
        ):

            with st.spinner(
                "Reading PDFs, creating chunks and generating embeddings..."
            ):

                try:

                    pages_data = []

                    for uploaded_file in uploaded_files:
                        pages_data.extend(
                            load_pdf(uploaded_file)
                        )

                    all_chunks = chunk_pages(
                        pages_data,
                        chunk_size=150,
                        overlap=30
                    )

                    if not all_chunks:

                        st.error(
                            "No readable text was found "
                            "in the uploaded PDF(s)."
                        )

                    else:

                        embeddings = create_document_embeddings(
                            all_chunks
                        )

                        index = create_faiss_index(
                            embeddings
                        )

                        st.session_state.all_chunks = all_chunks
                        st.session_state.index = index
                        st.session_state.processed_files = [
                            file.name for file in uploaded_files
                        ]

                        st.session_state.chat_history = []

                        st.success(
                            f"✅ Processing complete — "
                            f"{len(uploaded_files)} PDF(s), "
                            f"{len(all_chunks)} chunks created."
                        )

                except Exception as e:

                    st.error(
                        f"Error processing PDFs: {e}"
                    )


# =====================================================
# PROCESSED STATUS
# =====================================================

if "index" in st.session_state:

    st.markdown(
        f'<div class="status-card">'
        f'✅ Study material ready for questions'
        f' &nbsp; • &nbsp; '
        f'{len(st.session_state.all_chunks)} chunks indexed'
        f'</div>',
        unsafe_allow_html=True
    )


# =====================================================
# DOCUMENT DASHBOARD + QUICK START
# =====================================================

if "index" in st.session_state:
    processed_count = len(st.session_state.get("processed_files", []))
    chunk_count = len(st.session_state.get("all_chunks", []))

    st.markdown(
        '<div class="section-title">✨ Workspace Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">📄</div>'
            f'<div class="metric-value">{processed_count}</div>'
            f'<div class="metric-label">Documents</div></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">🧩</div>'
            f'<div class="metric-value">{chunk_count}</div>'
            f'<div class="metric-label">Text Chunks</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            '<div class="metric-card"><div class="metric-icon">🔎</div>'
            '<div class="metric-value">FAISS</div>'
            '<div class="metric-label">Similarity Search</div></div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            '<div class="metric-card"><div class="metric-icon">🤖</div>'
            '<div class="metric-value">Online</div>'
            '<div class="metric-label">Gemini AI</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="quick-card">'
        '<div class="quick-title">💡 Try asking CampusGPT</div>'
        '<div class="quick-sub">Choose a question or type your own below.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    q1, q2, q3 = st.columns(3)

    quick_questions = [
        ("📘", "What is DBMS?"),
        ("🔐", "Explain ACID properties."),
        ("🧩", "Explain the main concepts in this material.")
    ]

    for col, (icon, label) in zip([q1, q2, q3], quick_questions):
        with col:
            if st.button(f"{icon}  {label}", use_container_width=True):
                st.session_state.pending_question = label
                st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =====================================================
# CHAT HISTORY
# =====================================================

if st.session_state.chat_history:

    st.markdown(
        '<div class="section-title">💬 Conversation</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])

        else:

            with st.chat_message("assistant", avatar="🎓"):
                st.write(message["content"])

else:

    st.markdown(
        '<div class="info-card">'
        '<div style="font-size:22px;font-weight:800;color:#172033;">👋 Welcome to CampusGPT</div>'
        '<div style="color:#64748b;margin-top:7px;line-height:1.7;">'
        'Your study material is waiting. Upload a PDF above, process it, '
        'and start asking questions from your notes.'
        '</div>'
        '<div style="margin-top:14px;font-weight:700;color:#475569;">'
        '📄 Upload &nbsp;→&nbsp; 🧠 Process &nbsp;→&nbsp; 💬 Ask &nbsp;→&nbsp; 📚 Learn'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# =====================================================
# CHAT INPUT
# =====================================================

pending_question = st.session_state.pop("pending_question", None)

if pending_question:
    question = pending_question
else:
    question = st.chat_input(
        "Ask CampusGPT about your study material..."
    )


# =====================================================
# ASK CAMPUSGPT
# =====================================================

if question:

    if client is None:

        st.warning(
            "Please enter your Gemini API key in the sidebar."
        )

    elif "index" not in st.session_state:

        st.warning(
            "Please upload and process a PDF first."
        )

    else:

        # Display current user question

        with st.chat_message("user", avatar="👤"):
            st.write(question)

        # Search and answer

        with st.chat_message("assistant", avatar="🎓"):

            with st.spinner(
                "🔎 Searching your study material..."
            ):

                answer, sources = ask_question(
                    question,
                    st.session_state.all_chunks,
                    st.session_state.index,
                    k=3
                )

            st.write(answer)

            # Show sources in expandable section

            if sources:

                with st.expander("📚 Sources used"):

                    for source in sources:

                        st.markdown(
                            f'<div class="source-card">'
                            f'📄 <b>{source["source"]}</b>'
                            f' &nbsp; • &nbsp; '
                            f'Page <b>{source["page"]}</b>'
                            f' &nbsp; • &nbsp; '
                            f'Similarity '
                            f'<b>{source["score"]:.4f}</b>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

        # Save conversation

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="footer">'
    'CampusGPT • MCA Minor Project • '
    'RAG-based Student Learning Assistant'
    '</div>',
    unsafe_allow_html=True
)