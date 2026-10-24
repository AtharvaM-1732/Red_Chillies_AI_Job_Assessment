
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.document_processor import process_documents
from src.retrieval_engine import (
    setup_vector_store,
    build_conversational_retrieval_chain,
)

# PAGE CONFIG
st.set_page_config(
    page_title="Nexus AI | Enterprise RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# SESSION STATE
defaults = {
    "messages": [],
    "rag_chain": None,
    "indexed_chunks": 0,
    "indexed_files": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# CUSTOM CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --primary: #7868F6;
    --primary-light: #A99EFF;
    --bg-card: #171A25;
    --border: rgba(160, 165, 190, 0.16);
    --muted: #979CB1;
}

.stApp {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.7px;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 80% 0%, rgba(120,104,246,0.09), transparent 38%),
        var(--background-color);
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -1px;
    margin-bottom: 3px;
}

.brand span {
    color: var(--primary-light);
}

.eyebrow {
    color: var(--muted);
    font-size: 0.76rem;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    font-weight: 600;
}

.hero {
    padding: 28px 30px;
    border-radius: 22px;
    border: 1px solid var(--border);
    background: linear-gradient(
        120deg,
        rgba(120,104,246,0.15),
        rgba(120,104,246,0.025) 75%
    );
    margin: 12px 0 26px 0;
}

.hero h1 {
    font-size: clamp(2rem, 4vw, 3rem);
    line-height: 1.13;
    margin: 12px 0;
}

.hero p {
    color: var(--secondary-text-color);
    font-size: 1rem;
    line-height: 1.7;
    max-width: 650px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    border: 1px solid var(--border);
    border-radius: 100px;
    font-size: 0.8rem;
    background: rgba(120,104,246,0.08);
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #F0B65E;
    display: inline-block;
}

.status-dot.ready {
    background: #45D6A0;
    box-shadow: 0 0 10px rgba(69,214,160,0.4);
}

.metric-card {
    padding: 20px;
    min-height: 115px;
    border: 1px solid var(--border);
    border-radius: 17px;
    background: var(--secondary-background-color);
}

.metric-label {
    color: var(--muted);
    font-size: 0.83rem;
    margin-bottom: 12px;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
}

.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 30px 0 5px 0;
}

.section-subtitle {
    color: var(--muted);
    font-size: 0.88rem;
    margin-bottom: 18px;
}

.welcome-card {
    text-align: center;
    padding: 42px 24px;
    border: 1px dashed rgba(160,165,190,0.28);
    border-radius: 20px;
    margin: 15px 0;
    background: rgba(120,104,246,0.025);
}

.welcome-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.welcome-card h3 {
    font-size: 1.5rem;
    margin-bottom: 10px;
}

.welcome-card p {
    color: var(--muted);
    line-height: 1.7;
    max-width: 530px;
    margin: auto;
}

.source-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    margin: 10px 0;
    background: var(--secondary-background-color);
}

.source-label {
    color: var(--primary-light);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

.source-name {
    font-weight: 600;
    overflow-wrap: anywhere;
    margin-bottom: 8px;
}

.source-preview {
    color: var(--secondary-text-color);
    font-size: 0.86rem;
    line-height: 1.65;
}

div[data-testid="stChatMessage"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
}

.stButton > button {
    border-radius: 11px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7868F6, #6553DF);
    border: none;
    color: white;
}

.stButton > button[kind="primary"]:hover {
    filter: brightness(1.12);
    box-shadow: 0 5px 22px rgba(120,104,246,0.2);
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

[data-testid="stFileUploader"] {
    border: 1px dashed rgba(120,104,246,0.5);
    border-radius: 14px;
    padding: 8px;
}

hr {
    border-color: var(--border);
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# SIDEBAR
with st.sidebar:
    st.markdown(
        '<div class="brand">NEXUS<span>.AI</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("ENTERPRISE KNOWLEDGE ASSISTANT")
    st.divider()

    st.markdown("### 📂 Knowledge Base")
    st.caption("Upload your documents to create a searchable knowledge base.")

    uploaded_files = st.file_uploader(
        "Add documents",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Upload PDF or TXT files.",
    )

    if uploaded_files:
        st.caption(f"📄 {len(uploaded_files)} file(s) selected")

    if st.button(
        "⚡  Index Documents",
        type="primary",
        use_container_width=True,
    ):
        if not uploaded_files:
            st.warning("Please upload at least one PDF or TXT file.")
        else:
            try:
                with st.spinner("Processing documents and building the index..."):
                    chunks = process_documents(uploaded_files)

                    if not chunks:
                        st.warning("No text chunks were extracted from the documents.")
                    else:
                        qdrant_store = setup_vector_store(chunks)
                        new_chain = build_conversational_retrieval_chain(
                            chunks, qdrant_store
                        )

                        # Update session state only after successful setup.
                        st.session_state.rag_chain = new_chain
                        st.session_state.indexed_chunks = len(chunks)
                        st.session_state.indexed_files = [
                            file.name for file in uploaded_files
                        ]
                        st.session_state.messages = []

                        st.success(f"Successfully indexed {len(chunks)} chunks.")
                        st.rerun()

            except Exception as exc:
                st.error(f"Indexing failed: {exc}")

    st.divider()

    st.markdown("### ⚙️ System Status")

    is_ready = st.session_state.rag_chain is not None
    status_class = "ready" if is_ready else ""
    status_text = "Ready to answer" if is_ready else "Awaiting documents"

    st.markdown(
        f"""
        <div class="status-pill">
            <span class="status-dot {status_class}"></span>
            {status_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.caption(f"Indexed chunks: {st.session_state.indexed_chunks}")
    st.caption(f"Indexed files: {len(st.session_state.indexed_files)}")

    if st.session_state.indexed_files:
        with st.expander("View indexed files"):
            for filename in st.session_state.indexed_files:
                st.markdown(f"- 📄 {filename}")

    st.divider()

    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.caption("Nexus AI · Hybrid Retrieval · Conversational Memory")


# MAIN HEADER
is_ready = st.session_state.rag_chain is not None

st.markdown(
    """
    <div class="eyebrow">YOUR PRIVATE KNOWLEDGE WORKSPACE</div>
    <div class="hero">
        <div class="status-pill">
            <span class="status-dot ready"></span>
            PRIVATE DOCUMENT INTELLIGENCE
        </div>
        <h1>Knowledge, at your<br> fingertips.</h1>
        <p>
            Ask questions across your documents, uncover relevant information,
            and explore cited source passages through one intelligent workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# METRICS
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📚 Indexed chunks</div>
            <div class="metric-value">{st.session_state.indexed_chunks:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📄 Documents</div>
            <div class="metric-value">{len(st.session_state.indexed_files):,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">💬 Messages</div>
            <div class="metric-value">{len(st.session_state.messages):,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-heading">AI Conversation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Ask questions and explore your indexed knowledge.</div>',
    unsafe_allow_html=True,
)

# CHAT HISTORY
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(
        message["role"],
        avatar="🧑‍💻" if message["role"] == "user" else "🧠",
    ):
        st.markdown(message["content"])

        # Render saved source excerpts when available.
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander(
                f"📚 Explore sources ({len(message['sources'])})"
            ):
                for i, source in enumerate(message["sources"], start=1):
                    st.markdown(
                        f"""
                        <div class="source-card">
                            <div class="source-label">SOURCE {i}</div>
                            <div class="source-name">{source['name']}</div>
                            <div class="source-preview">
                                {source['preview']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# WELCOME SCREEN & SUGGESTED PROMPTS
if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-icon">✦</div>
            <h3>What would you like to discover?</h3>
            <p>
                Ask a question about your indexed documents. Nexus AI will
                retrieve relevant passages and use them to formulate an answer.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt_cols = st.columns(3)
    suggestions = [
        ("📝  Summarize", "Summarize the key points in my documents."),
        ("🔎  Find details", "What are the most important details in the documents?"),
        ("📊  Compare", "Compare the main concepts discussed in my documents."),
    ]

    for col, (label, prompt) in zip(prompt_cols, suggestions):
        with col:
            if st.button(label, use_container_width=True, disabled=not is_ready):
                st.session_state.pending_prompt = prompt
                st.rerun()


# CHAT INPUT & RESPONSE
user_query = st.chat_input(
    "Ask anything about your documents...",
    disabled=not is_ready,
)

# Handle suggestion-button prompts on the next rerun.
if not user_query and st.session_state.get("pending_prompt"):
    user_query = st.session_state.pop("pending_prompt")

if user_query:
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_query)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Searching knowledge and generating an answer..."):
            try:
                chat_history = []

                for msg in st.session_state.messages[:-1]:
                    if msg["role"] == "user":
                        chat_history.append(
                            HumanMessage(content=msg["content"])
                        )
                    elif msg["role"] == "assistant":
                        chat_history.append(
                            AIMessage(content=msg["content"])
                        )

                response = st.session_state.rag_chain.invoke({
                    "input": user_query,
                    "chat_history": chat_history,
                })

                answer = response.get(
                    "answer",
                    "I couldn't generate an answer for this question.",
                )

                st.markdown(answer)

                sources = []

                for doc in response.get("context", []):
                    raw_name = doc.metadata.get("source", "Unknown source")
                    source_name = str(raw_name).replace("\\", "/").split("/")[-1]
                    preview = doc.page_content[:1000]

                    sources.append({
                        "name": source_name,
                        "preview": preview,
                    })

                if sources:
                    with st.expander(f"📚 Explore sources ({len(sources)})"):
                        for i, source in enumerate(sources, start=1):
                            st.markdown(
                                f"""
                                <div class="source-card">
                                    <div class="source-label">SOURCE {i}</div>
                                    <div class="source-name">{source['name']}</div>
                                    <div class="source-preview">
                                        {source['preview']}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except Exception as exc:
                st.error(f"Unable to generate a response: {exc}")
                st.info("Check that the retrieval chain and vector store are configured correctly.")
