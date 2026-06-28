# Meeting Assistant

Meeting Assistant is a web application that helps you process your meeting recordings. You can upload an audio or video file, and the app will automatically chop it, transcribe it into text, create a professional title, write a summary report, and let you ask questions about the meeting.

**Live Application Link:** [Click here to use Meeting Assistant](https://meeting-assistantgit-qg6uvapagbfcejnpzjjvmv.streamlit.app/)

---

## What It Does

* [cite_start]**Audio Processing:** Cuts large files into small 2-minute parts using `ffmpeg`[cite: 1, 2].
* [cite_start]**Transcription:** Converts spoken audio into text using an AI speech-to-text model.
* [cite_start]**Smart Summary:** Creates an organized report with a Summary, Action Items, Key Decisions, and Open Questions.
* [cite_start]**Meeting Chat:** Builds a local knowledge base from the text so you can ask specific questions and get exact answers.

---

## Tech Stack Used

This project uses the following tools and libraries:

* [cite_start]**Frontend UI:** `Streamlit` (to build the web page interface).
* [cite_start]**AI Orchestration:** `LangChain`, `LangChain-Core`, `LangChain-Community`, and `LangChain-Groq` (to manage prompts, tools, and AI text processing).
* [cite_start]**LLM & API Provider:** `Groq Cloud API` running the `meta-llama/llama-4-scout-17b-16e-instruct` model for text tasks.
* [cite_start]**Speech-to-Text:** `Whisper-Large-v3` (via Groq API) to transcribe the audio chunks.
* [cite_start]**Vector Database:** `FAISS` (CPU version) to store text snippets for the chat function.
* [cite_start]**Text Embeddings:** `HuggingFaceEmbeddings` using the `all-MiniLM-L6-v2` model from `Sentence-Transformers`.
* [cite_start]**Deep Learning Backend:** `PyTorch` (`torch`).
* [cite_start]**Data & Science Tools:** `NumPy`, `Pandas`, and `SciPy`.
* [cite_start]**Audio Media Tool:** `ffmpeg` (system package) [cite: 1, 2] [cite_start]and `pydub` (python library).
* [cite_start]**Environment Management:** `python-dotenv`.

---

## How to Setup and Run

### 1. Install System Requirements
[cite_start]You must have `ffmpeg` installed on your computer system to cut the audio files[cite: 1, 2].

### 2. Install Python Packages
[cite_start]Install all required python libraries using the requirements file:
```bash
pip install -r requirements.txt