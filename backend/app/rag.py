"""
TripGenie AI — Modular Retrieval-Augmented Generation (RAG) Engine.

Academic Architecture (Clean 8-Stage Pipeline):
1. User Query
2. Query Processing (Normalization, Intent & Entity Extraction)
3. Embedding Generation (Sentence-Transformers all-MiniLM-L6-v2, 384-dim)
4. Vector Storage & Indexing (In-memory normalized float32 matrix)
5. Vector Similarity Search (Normalized Cosine Dot-Product)
6. Context & Metadata Filtering (Destination Relevance Boosting & Category Filtering)
7. Top-K Retrieval & Source Tracking (Provenance tracking for explainability)
8. Context Formatting (Structured text injection for LLM prompt construction)
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from app.knowledge_base import TRAVEL_DOCUMENTS
from app.config import EMBEDDING_MODEL, TOP_K_RESULTS


class QueryProcessor:
    """Stage 1: Cleans raw query text and extracts entity/filter hints."""
    
    @staticmethod
    def process(query: str, destination: Optional[str] = None) -> Dict[str, Any]:
        cleaned = re.sub(r"[^\w\s\-,]", " ", query.strip())
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Detect interest / category keywords
        categories = []
        lower_q = cleaned.lower()
        if any(w in lower_q for w in ["beach", "water", "sport", "scuba", "rafting", "temple", "fort", "attraction", "visit", "see"]):
            categories.append("attractions")
        if any(w in lower_q for w in ["food", "dish", "eat", "curry", "thali", "restaurant", "seafood", "cuisine"]):
            categories.append("food")
        if any(w in lower_q for w in ["stay", "hotel", "resort", "hostel", "cottage", "camp", "tent"]):
            categories.append("stay")
        if any(w in lower_q for w in ["budget", "cost", "price", "rupee", "cheap", "expense"]):
            categories.append("budget")
        if any(w in lower_q for w in ["time", "season", "weather", "month", "pack", "tip", "permit"]):
            categories.append("tips")

        return {
            "raw_query": query,
            "cleaned_query": cleaned,
            "target_destination": destination.strip() if destination else None,
            "suggested_categories": categories,
        }


class EmbeddingManager:
    """Stage 2: Generates dense semantic vector representations."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode_documents(self, texts: List[str]) -> np.ndarray:
        """Embeds document corpus into normalized vectors."""
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def encode_query(self, query: str) -> np.ndarray:
        """Embeds a single query into a 384-dimensional normalized vector."""
        return self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]


class VectorStore:
    """Stage 3 & 4: In-Memory Vector Storage and Cosine Similarity Index."""

    def __init__(self, documents: List[Dict[str, Any]], embedding_mgr: EmbeddingManager):
        self.documents = documents
        self.embedding_mgr = embedding_mgr
        self.index: Optional[np.ndarray] = None
        self._build_index()

    def _build_index(self):
        """Encodes all document chunks into an in-memory float32 matrix."""
        corpus_texts = []
        for doc in self.documents:
            # Combine place_name, activities, description, and tips for maximum semantic coverage
            semantic_text = doc.get("text") or (
                f"{doc.get('place_name', '')} in {doc.get('destination', '')} ({doc.get('category', '')}). "
                f"{doc.get('description', '')} Activities: {', '.join(doc.get('activities', []))}. "
                f"Tips: {doc.get('travel_tips', '')}"
            )
            corpus_texts.append(semantic_text)

        embeddings = self.embedding_mgr.encode_documents(corpus_texts)
        self.index = np.array(embeddings, dtype=np.float32)

    def search(self, query_vector: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity against all stored chunks.
        Since both query and document vectors are L2-normalized,
        matrix dot product directly computes the cosine similarity score.
        """
        if self.index is None:
            raise RuntimeError("Vector store index is not initialized.")
        return self.index @ query_vector


class ContextFilter:
    """Stage 5 & 6: Metadata Filtering, Destination Boosting, and Top-K Selection."""

    @staticmethod
    def filter_and_rank(
        scores: np.ndarray,
        documents: List[Dict[str, Any]],
        destination: Optional[str] = None,
        categories: Optional[List[str]] = None,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Dict[str, Any]]:
        ranked_scores = scores.copy()

        # Heuristic Destination Boosting (+0.15 for exact or partial destination matches)
        if destination:
            dest_lower = destination.lower()
            for i, doc in enumerate(documents):
                doc_dest = doc.get("destination", "").lower()
                if doc_dest == dest_lower or dest_lower in doc_dest or doc_dest in dest_lower:
                    ranked_scores[i] += 0.15

        # Optional Category Boosting
        if categories:
            cat_set = {c.lower() for c in categories}
            for i, doc in enumerate(documents):
                if doc.get("category", "").lower() in cat_set:
                    ranked_scores[i] += 0.05

        # Rank indices in descending order of similarity
        top_indices = np.argsort(ranked_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = documents[int(idx)]
            results.append({
                "id": doc.get("id", f"chunk-{idx}"),
                "destination": doc.get("destination"),
                "place_name": doc.get("place_name"),
                "category": doc.get("category"),
                "description": doc.get("description"),
                "location": doc.get("location"),
                "activities": doc.get("activities", []),
                "estimated_cost": doc.get("estimated_cost"),
                "best_time": doc.get("best_time"),
                "duration": doc.get("duration"),
                "travel_tips": doc.get("travel_tips"),
                "text": doc.get("text"),
                "score": float(ranked_scores[idx]),
                "raw_cosine_score": float(scores[idx]),
            })
        return results


class ContextFormatter:
    """Stage 7: Formats retrieved chunks into clean structured text blocks for LLM prompt injection."""

    @staticmethod
    def format(chunks: List[Dict[str, Any]]) -> str:
        blocks = []
        for idx, c in enumerate(chunks, 1):
            place = c.get("place_name") or c.get("destination")
            cat = c.get("category", "general")
            desc = c.get("description") or c.get("text")
            acts = ", ".join(c.get("activities", []))
            tips = c.get("travel_tips", "")
            cost = c.get("estimated_cost", "")

            block = f"[{idx}] {place} ({c.get('destination')} / {cat})\n"
            block += f"    Details: {desc}\n"
            if acts:
                block += f"    Activities: {acts}\n"
            if cost:
                block += f"    Cost: {cost}\n"
            if tips:
                block += f"    Tip: {tips}\n"
            blocks.append(block.strip())
        return "\n\n".join(blocks)


class RAGEngine:
    """
    Main Controller for the 8-Stage TripGenie AI RAG Pipeline.
    Singleton built once at startup and shared across endpoints.
    """

    def __init__(self):
        self.documents = TRAVEL_DOCUMENTS
        self.embedding_mgr = EmbeddingManager()
        self.vector_store = VectorStore(self.documents, self.embedding_mgr)

    def retrieve(
        self,
        query: str,
        destination: Optional[str] = None,
        categories: Optional[List[str]] = None,
        k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Executes full RAG retrieval pipeline and returns ranked chunks."""
        top_k = k or TOP_K_RESULTS

        # 1. Query Processing
        processed = QueryProcessor.process(query, destination=destination)

        # 2. Embedding Generation
        query_vec = self.embedding_mgr.encode_query(processed["cleaned_query"])

        # 3. Vector Similarity Search (Cosine)
        scores = self.vector_store.search(query_vec)

        # 4. Context Filtering & Top-K Ranking
        results = ContextFilter.filter_and_rank(
            scores=scores,
            documents=self.documents,
            destination=destination,
            categories=categories or processed["suggested_categories"],
            top_k=top_k,
        )

        return results

    def get_grounded_context(
        self, query: str, destination: Optional[str] = None, k: Optional[int] = 8
    ) -> str:
        """Returns formatted string context ready for direct prompt injection."""
        chunks = self.retrieve(query, destination=destination, k=k)
        return ContextFormatter.format(chunks)

    def explain_retrieval(self, query: str, destination: Optional[str] = None) -> Dict[str, Any]:
        """Provides transparency and explainability metrics for academic viva evaluations."""
        processed = QueryProcessor.process(query, destination=destination)
        chunks = self.retrieve(query, destination=destination, k=5)
        return {
            "query_analysis": processed,
            "embedding_model": self.embedding_mgr.model_name,
            "vector_dimension": 384,
            "total_documents_indexed": len(self.documents),
            "top_retrieved_chunks": [
                {
                    "chunk_id": c["id"],
                    "place_name": c["place_name"],
                    "category": c["category"],
                    "combined_score": round(c["score"], 3),
                    "raw_cosine": round(c["raw_cosine_score"], 3),
                }
                for c in chunks
            ],
        }

    def known_destinations(self) -> List[str]:
        """Returns list of unique destinations covered in the vector store."""
        return sorted({doc["destination"] for doc in self.documents})


# Global singleton instance built once at process start
rag_engine = RAGEngine()
