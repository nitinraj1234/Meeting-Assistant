import os
import time
import subprocess
from dotenv import load_dotenv
from groq import Groq

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_CHARS = 20000


class MeetingAgent:

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.3
        )
        self.vector_store = None
        self.transcript = None
        self.analysis = None

    def process_input(self, source: str) -> list:
        chunks = []
        i = 0
        while True:
            output_path = os.path.join(DOWNLOAD_DIR, f"chunk_{i}.mp3")
            start_seconds = i * 2 * 60
            result = subprocess.run([
                "ffmpeg",
                "-ss", str(start_seconds),
                "-i", source,
                "-t", str(2 * 60),
                "-ar", "16000",
                "-ac", "1",
                "-ab", "64k",
                "-f", "mp3",
                "-y",
                output_path
            ], capture_output=True)

            if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
                break

            chunks.append(output_path)
            i = i + 1

        return chunks

    def transcribe_all(self, chunks: list) -> str:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        full_transcript = ""

        for chunk_path in chunks:
            with open(chunk_path, "rb") as f:
                file_content = f.read()

            response = client.audio.transcriptions.create(
                file=(os.path.basename(chunk_path), file_content),
                model="whisper-large-v3",
                response_format="text"
            )

            full_transcript = full_transcript + response + " "

        self.transcript = full_transcript.strip()
        return self.transcript

    def generate_title(self, transcript: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a short professional meeting title (max 8 words). Return only the title."),
            ("human", "{text}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"text": transcript[:2000]})

    def analyze_meeting(self, transcript: str) -> str:
        system_prompt = """Analyze this meeting section and provide:

1. Summary:
   Summarize only the information discussed.

2. Action Items:
   List only tasks assigned or agreed upon.

3. Key Decisions:
   List only decisions explicitly made.

4. Open Questions:
   List only unresolved questions explicitly discussed.
   Do not infer or create questions.

If a section has no information, write:
'None identified.'

Use clear headings."""

        combine_prompt = """Merge these meeting analyses into one final report with:

1. Summary
2. Action Items
3. Key Decisions
4. Open Questions

Rules:
- Remove duplicates.
- Do not introduce new information.
- Do not infer missing details.
- Preserve only information present in the chunk analyses.
- If a section has no information, write 'None identified.'

Use clear headings and bullet points."""

        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}")
        ])
        analysis_chain = analysis_prompt | self.llm | StrOutputParser()

        parts = []
        i = 0
        while i < len(transcript):
            parts.append(transcript[i:i + MAX_CHARS])
            i = i + MAX_CHARS

        if len(parts) == 1:
            self.analysis = analysis_chain.invoke({"text": parts[0]})
            return self.analysis

        results = []

        for part in parts:
            success = False
            while not success:
                try:
                    result = analysis_chain.invoke({"text": part})
                    results.append(result)
                    success = True
                except Exception as e:
                    if "rate_limit_exceeded" in str(e):
                        time.sleep(60)
                    else:
                        raise

        combine_prompt_template = ChatPromptTemplate.from_messages([
            ("system", combine_prompt),
            ("human", "{text}")
        ])
        combine_chain = combine_prompt_template | self.llm | StrOutputParser()

        self.analysis = combine_chain.invoke({"text": "\n\n".join(results)})
        return self.analysis

    def build_vector_store(self, transcript: str):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300, separators=["\n\n", "\n", ". ", " ", ""])
        chunks = splitter.split_text(transcript)
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
        self.vector_store = FAISS.from_texts(chunks, embeddings)

    def ask(self, question: str) -> str:
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 15}
        )

        docs = retriever.invoke(question)

        context = ""
        for doc in docs:
            context = context + doc.page_content + "\n\n"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meeting assistant.
Answer using the meeting summary and the detailed context provided below.
Rules:
- Do not use outside knowledge.
- Do not guess or assume.
- Do not infer facts that are not explicitly stated.
- If the answer is not present in either the summary or the context, reply exactly:
  'I could not find this information in the meeting transcript.'"""),
            ("human", "Meeting Summary:\n{summary}\n\nDetailed Context:\n{context}\n\nQuestion:\n{question}")
        ])
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({"summary": self.analysis, "context": context, "question": question})