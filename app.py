import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 24px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
}

.block-container {
    padding-top: 2rem;
}

.summary-box {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #374151;
}

.metric-card {
    background: #1f2937;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("🎥 AI Video Assistant")
st.caption("Summarize meetings, extract insights, and chat with your videos.")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:
    st.header("⚙️ Settings")

    language = st.selectbox(
        "Select Language",
        ["english", "hinglish"],
    )

    st.divider()

    st.markdown("""
    ### Features
    ✅ AI Summary  
    ✅ Action Items  
    ✅ Key Decisions  
    ✅ Open Questions  
    ✅ RAG Chat  
    """)

# ---------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    youtube_url = st.text_input(
        "📺 YouTube URL",
        placeholder="Paste YouTube link..."
    )

with col2:
    uploaded_file = st.file_uploader(
        "📂 Upload Audio/Video",
        type=["mp3", "wav", "mp4", "m4a"]
    )

# ---------------------------------------------------
# PROCESS BUTTON
# ---------------------------------------------------

if st.button("🚀 Process Content", use_container_width=True):

    source = None

    # Determine source
    if youtube_url:
        source = youtube_url

    elif uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        source = temp_path

    else:
        st.warning("Please provide a YouTube URL or upload a file.")
        st.stop()

    # Progress UI
    progress = st.progress(0)
    status = st.empty()

    # ---------------------------------------------------
    # PIPELINE
    # ---------------------------------------------------

    try:

        status.info("🎧 Processing audio...")
        chunks = process_input(source)
        progress.progress(15)

        status.info("📝 Transcribing...")
        transcript = transcribe_all(chunks, language)
        progress.progress(40)

        status.info("🧠 Generating summary...")
        title = generate_title(transcript)
        summary = summarize(transcript)
        progress.progress(60)

        status.info("📌 Extracting insights...")
        action_items = extract_action_items(transcript)
        decisions = extract_key_decisions(transcript)
        questions = extract_questions(transcript)
        progress.progress(80)

        status.info("🔎 Building RAG engine...")
        rag_chain = build_rag_chain(transcript)
        progress.progress(100)

        status.success("✅ Processing Completed!")

        # Store in session state
        st.session_state["rag_chain"] = rag_chain
        st.session_state["transcript"] = transcript

        # ---------------------------------------------------
        # TITLE
        # ---------------------------------------------------

        st.header(f"📌 {title}")

        # ---------------------------------------------------
        # METRICS
        # ---------------------------------------------------

        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric("Transcript Length", f"{len(transcript)} chars")

        with m2:
            st.metric("Action Items", len(action_items.split("\n")))

        with m3:
            st.metric("Questions", len(questions.split("\n")))

        # ---------------------------------------------------
        # TABS
        # ---------------------------------------------------

        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Summary",
            "✅ Action Items",
            "🔑 Decisions",
            "📝 Transcript"
        ])

        with tab1:
            st.markdown("## 📋 Summary")
            st.write(summary)

            st.markdown("## ❓ Open Questions")
            st.write(questions)

        with tab2:
            st.markdown("## ✅ Action Items")
            st.write(action_items)

        with tab3:
            st.markdown("## 🔑 Key Decisions")
            st.write(decisions)

        with tab4:
            st.markdown("## 📝 Full Transcript")
            st.text_area(
                "Transcript",
                transcript,
                height=400
            )

        # ---------------------------------------------------
        # DOWNLOADS
        # ---------------------------------------------------

        st.divider()

        st.subheader("⬇️ Download Results")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download Summary",
                summary,
                file_name="summary.txt"
            )

        with col2:
            st.download_button(
                "Download Transcript",
                transcript,
                file_name="transcript.txt"
            )

    except Exception as e:
        st.error(f"Error: {str(e)}")

# ---------------------------------------------------
# RAG CHAT SECTION
# ---------------------------------------------------

if "rag_chain" in st.session_state:

    st.divider()
    st.header("💬 Chat With Your Meeting")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    prompt = st.chat_input("Ask something about the meeting...")

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                answer = ask_question(
                    st.session_state["rag_chain"],
                    prompt
                )

            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })