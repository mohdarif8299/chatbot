from app.services.redis_service import RedisService
from app.services.db_service import DatabaseService
from app.services.pinecone_service import PineconeService
from app.config import Config
import hashlib
import datetime
import openai
import fitz 
import docx 
import io

class RAGService:
    def __init__(self):
        self.db = DatabaseService()
        self.pinecone = PineconeService()
        self.redis = RedisService()
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def embed(self, text):
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def chunk_content(self, text, chunk_size=300):
        words = text.split()
        return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    def extract_pdf_text(self, file_bytes):
        text = ""
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        for page in pdf:
            text += page.get_text()
        return text

    def extract_docx_text(self, file_bytes):
        text = ""
        file_stream = io.BytesIO(file_bytes)
        doc = docx.Document(file_stream)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def process_content(self, file_bytes, filename):
        text = ""

        if filename.lower().endswith('.pdf'):
            text = self.extract_pdf_text(file_bytes)
        elif filename.lower().endswith('.docx'):
            text = self.extract_docx_text(file_bytes)
        else:
            raise ValueError("Unsupported file format. Only PDF and DOCX are allowed.")

        chunks = self.chunk_content(text)
        vectors = []

        for i, chunk in enumerate(chunks):
            vector = self.embed(chunk)
            chunk_id = hashlib.md5((filename + str(i)).encode()).hexdigest()
            vectors.append({"id": chunk_id, "values": vector, "metadata": {"text": chunk}})

        self.pinecone.upsert_vectors(vectors)
        return chunks

    def retrieve(self, question):
        vector = self.embed(question)
        results = self.pinecone.query(vector)
        contexts = [m['metadata']['text'] for m in results['matches']]
        return contexts

    def answer(self, question, content_id):
        cached_answer = self.redis.get_cached_answer(content_id, question)
        if cached_answer:
            return cached_answer

        contexts = self.retrieve(question)
        context = "\n".join(contexts)

        system_prompt = (
            "You are an expert teacher helping students understand the topic. "
            "Use simple explanations, relevant examples, and make sure the student can grasp the concept. "
            "Avoid unnecessary jargon. Use short paragraphs. If possible, relate the explanation to real-world scenarios."
        )

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Student Question: {question}\n\n"
            "Teacher Explanation:"
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content
        self.redis.set_cached_answer(content_id, question, answer)
        return answer
