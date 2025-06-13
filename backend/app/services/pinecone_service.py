import pinecone
from app.config import Config

class PineconeService:
    def __init__(self):
        self.pc = pinecone.Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self.pc.Index(Config.PINECONE_INDEX)

    def upsert_vectors(self, vectors: list[dict]):
        self.index.upsert(vectors=vectors)

    def query(self, vector: list[float], top_k: int = 3):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )