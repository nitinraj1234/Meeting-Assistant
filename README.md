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
## How the App Works Step-by-Step

When you upload a file and click the **"Process & Analyse"** button, the backend code executes a complete data pipeline from start to finish. Here is the highly detailed breakdown of what happens under the hood:

### 1. File Upload and Local Storage
* **File Ingestion:** The `Streamlit` frontend interface accepts your media file (supporting formats like `.mp3`, `.mp4`, `.wav`, `.m4a`, or `.webm`).
* **Saving to Disk:** The app reads the binary data stream of the file and writes it onto your machine's storage inside a folder named `downloads/` using its original filename. This acts as the raw source file for the next step.

### 2. Audio Splitting and Optimization (The Process Input Stage)
* **Background Worker:** The app initializes a loop that runs a system-level tool named `ffmpeg` via Python's `subprocess` library.
* **Chop into 2-Minute Intervals:** It reads the raw file and cuts it into sequential, small audio files named `chunk_0.mp3`, `chunk_1.mp3`, `chunk_2.mp3`, etc.
* **Audio Compression:** While chopping, `ffmpeg` automatically compresses each chunk to save bandwidth and keep API calls fast. It converts the audio to a **16,000Hz sampling rate**, sets it to **mono channel** (1 audio channel), and lowers the bitrate to **64kbps**.
* **Exit Condition:** The loop checks the file size of each generated chunk. When `ffmpeg` creates an empty file or a chunk smaller than 1000 bytes, the loop knows it reached the end of the meeting and stops. All active chunk file paths are saved into a list.

### 3. Audio Transcription (The Speech-to-Text Stage)
* **Groq API Connection:** The app sets up a connection to the Groq Cloud Service using your secret `GROQ_API_KEY`.
* **Sequential Processing:** The code loops through your list of 2-minute `.mp3` files one by one. It reads each file and uploads it to Groq's servers.
* **Whisper Processing:** It calls the **`whisper-large-v3`** model to process the audio chunk and convert the spoken words into raw text strings.
* **Transcript Merging:** As each chunk finishes transcribing, its text is appended to a master string variable (`full_transcript`) with a blank space separating them. Once all chunks are completed, `.strip()` is used to clean up any trailing empty spaces, giving you the final full meeting transcript.

### 4. Meeting Title Generation
* **Context Fetching:** To save time and API costs, the app takes just the first 2,000 characters of the new full transcript.
* **AI Instructions:** It wraps this text snippet inside a strict prompt instruction: *"Generate a short professional meeting title (max 8 words). Return only the title."*
* **Llama Processing:** The prompt is sent to the **`meta-llama/llama-4-scout-17b-16e-instruct`** model via LangChain. The model returns just the title string, which is immediately updated on the Streamlit screen header.

### 5. Meeting Analysis & Summary (The Map-Reduce Loop)
* **Text Chunks for LLM:** A large text transcript can easily overload an AI model's context or rate limits. To prevent this, the code splits the full text into large blocks of **20,000 characters** each.
* **The Map Step (Individual Block Analysis):** For each 20,000-character block, the app asks the Llama model to compile 4 specific sections: *Summary, Action Items, Key Decisions, and Open Questions*. If a section doesn't have relevant data, the model outputs *"None identified."*
* **Rate Limit Fail-Safe:** If the Groq API sends back a `rate_limit_exceeded` error because the text blocks are being processed too quickly, the code halts, sleeps for **60 seconds**, and automatically tries that block again so the app never crashes.
* **The Reduce Step (Final Consolidation):** Once all individual blocks are analyzed, their summaries are joined together. The app passes this collective text to the Llama model one last time with strict rules to remove duplicate points, remove any outside assumptions, and merge everything into a single, clean report.

### 6. Building the Knowledge Base (The Vector Search Setup)
To allow you to chat with your transcript, the app builds a searchable mathematical index:
* **Text Splitting:** The full text transcript is broken down into small, overlapping snippets of **1200 characters** each, with a **300-character overlap** (the overlap ensures sentences cut off in one snippet are preserved completely in the next).
* **Creating Embeddings:** Each snippet is fed into a Hugging Face sentence transformer model called **`all-MiniLM-L6-v2`**. This model runs on your machine's CPU via **PyTorch** and translates the human words into an array of numbers (a vector) representing its semantic meaning.
* **The FAISS Database:** These number vectors are loaded into a **FAISS** (Facebook AI Similarity Search) index database. This index is saved directly into the Streamlit session state memory.

### 7. Asking Questions (The RAG Chat System)
* **User Query:** When you type a question into the chat input bar, the app doesn't send the entire transcript to the AI. 
* **Semantic Search:** First, your question is turned into a vector using the same Hugging Face model. FAISS compares your question vector against all the stored meeting snippets and instantly pulls out the **top 15 closest matching text snippets** (`k=15`).
* **Context Assembly:** These 15 relevant snippets are merged into a clean text block called `Detailed Context`.
* **Final AI Answer:** The app builds a prompt containing the **Final Report Summary**, the **Detailed Context**, and your **Question**. It gives strict instructions to the Llama model to answer using *only* that text, map matching meanings rather than just exact words, attribute statements to the correct speaker, and say *"I could not find this information in the meeting transcript."* if it isn't explicitly there.

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
