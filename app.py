import os
import streamlit as st
from dotenv import load_dotenv
from agent import MeetingAgent

load_dotenv()

st.set_page_config(
    page_title="Meeting Assistant",
    layout="wide"
)

if "agent" not in st.session_state:
    st.session_state.agent = MeetingAgent()
    st.session_state.result = None
    st.session_state.chat_messages = []

agent = st.session_state.agent


st.title("Meeting Assistant")
st.caption("Transcribe, summarize, and chat with your meeting")

st.divider()


uploaded_file = st.file_uploader(
    "Upload your meeting audio or video file",
    type=["mp4", "mp3", "wav", "m4a", "webm"]
)
st.caption("💡 For best results upload mp3. 1hr meeting ≈ 60MB.")

if st.button("Process & Analyse", type="primary"):

    if uploaded_file is None:
        st.warning("Please upload a file.")

    else:
        try:
            temp_path = os.path.join("downloads", uploaded_file.name)
            os.makedirs("downloads", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner("Processing audio..."):
                chunks = agent.process_input(temp_path)

            with st.spinner("Transcribing..."):
                transcript = agent.transcribe_all(chunks)

            with st.spinner("Generating title..."):
                title = agent.generate_title(transcript)

            with st.spinner("Analysing meeting..."):
                analysis = agent.analyze_meeting(transcript)

            with st.spinner("Building knowledge base..."):
                agent.build_vector_store(transcript)

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "analysis": analysis,
            }

            st.session_state.chat_messages = []
            st.success("Done!")

        except Exception as e:
            st.error(str(e))

st.divider()


if st.session_state.result:

    result = st.session_state.result

    st.header(result["title"])

    left, right = st.columns([1, 1])

    with left:
        tab1, tab2 = st.tabs(["Analysis", "Transcript"])

        with tab1:
            st.markdown(result["analysis"])

        with tab2:
            st.text_area("Full Transcript", result["transcript"], height=500)

    with right:
        st.subheader("Ask about your meeting")
        st.caption("Each question is answered independently from the transcript.")

        chat_container = st.container(height=500)

        with chat_container:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        question = st.chat_input("Ask anything about the meeting...")

        if question:
            st.session_state.chat_messages.append({
                "role": "user",
                "content": question
            })

            answer = agent.ask(question)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer
            })

            st.rerun()
