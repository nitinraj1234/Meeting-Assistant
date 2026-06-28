# Meeting Assistant

Meeting Assistant is a web application that helps you process your meeting recordings. You can upload an audio or video file, and the app will automatically chop it, transcribe it into text, create a professional title, write a summary report, and let you ask questions about the meeting.

**Live Application Link:** [Click here to use Meeting Assistant](https://meeting-assistantgit-qg6uvapagbfcejnpzjjvmv.streamlit.app/)

---

## What It Does

* **Audio Processing:** Cuts large files into small 2-minute parts using `ffmpeg`.
* **Transcription:** Converts spoken audio into text using an AI speech-to-text model.
* **Smart Summary:** Creates an organized report with a Summary, Action Items, Key Decisions, and Open Questions.
* **Meeting Chat:** Builds a local knowledge base from the text so you can ask specific questions and get exact answers.

---

## Tech Stack Used

This project uses the following tools and libraries:

* **Frontend UI:** `Streamlit` (to build the web page interface).
* **AI Orchestration:** `LangChain`, `LangChain-Core`, `LangChain-Community`, and `LangChain-Groq` (to manage prompts, tools, and AI text processing).
* **LLM & API Provider:** `Groq Cloud API` running the `meta-llama/llama-4-scout-17b-16e-instruct` model for text tasks.
* **Speech-to-Text:** `Whisper-Large-v3` (via Groq API) to transcribe the audio chunks.
* **Vector Database:** `FAISS` (CPU version) to store text snippets for the chat function.
* **Text Embeddings:** `HuggingFaceEmbeddings` using the `all-MiniLM-L6-v2` model from `Sentence-Transformers`.
* **Deep Learning Backend:** `PyTorch` (`torch`).
* **Data & Science Tools:** `NumPy`, `Pandas`, and `SciPy`.
* **Audio Media Tool:** `ffmpeg` (system package) and `pydub` (python library).
* **Environment Management:** `python-dotenv`.

---
