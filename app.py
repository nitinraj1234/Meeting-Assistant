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



left_head, right_head = st.columns([3, 1])

with left_head:
    st.title("Meeting Assistant")
    st.caption("Transcribe, summarize, and chat with your meeting")

with right_head:
    with st.expander("📂 How to get file path"):
        st.markdown("""
**Mac**
- Hold `Option`
- Right click file
- Copy "file" as Pathname

**Windows**
- Hold `Shift`
- Right click file
- Copy as path
        """)

st.divider()



source = st.text_input(
    "YouTube URL or local file path",
    placeholder="https://youtube.com/... or /path/to/file.mp4"
)

if st.button("Process & Analyse", type="primary"):

    if not source.strip():
        st.warning("Please enter a YouTube URL or local file path.")

    else:

        with st.spinner("Processing audio..."):
            chunks = agent.process_input(source.strip())

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