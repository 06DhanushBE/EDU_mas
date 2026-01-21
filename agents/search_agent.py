"""
Search Agent - Semantic search powered by Qdrant vector database
"""

import os
from typing import Tuple, List, Dict
from groq import Groq
from utils.qdrant_client import QdrantManager


class SearchAgent:
    """
    Specialized agent for semantic search across book content.
    Uses Qdrant for vector similarity search.
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.qdrant = QdrantManager()
    
    def semantic_search(self, query: str) -> Tuple[str, List[Dict]]:
        """Perform semantic search and generate answer"""
        logs = []
        
        logs.append({
            "agent": "search",
            "action": f"Initiating semantic search: {query[:50]}...",
            "timestamp": self._get_timestamp()
        })
        
        # Perform Qdrant vector search
        logs.append({
            "agent": "search",
            "action": "Searching Qdrant vector database",
            "qdrant_query": query,
            "timestamp": self._get_timestamp()
        })
        
        search_results = self.qdrant.search(query, limit=5)
        
        logs.append({
            "agent": "search",
            "action": f"Found {len(search_results)} relevant passages",
            "timestamp": self._get_timestamp()
        })
        
        if not search_results:
            return "I couldn't find relevant information in the book. Try rephrasing your question!", logs
        
        # Generate answer from retrieved context
        logs.append({
            "agent": "search",
            "action": "Generating answer with Groq LLM",
            "timestamp": self._get_timestamp()
        })
        
        context = "\n\n".join([
            f"[Passage {i+1}]: {item['text']}"
            for i, item in enumerate(search_results)
        ])
        
        prompt = f"""You are answering questions about "Rich Dad Poor Dad" by Robert Kiyosaki.

User Question: {query}

Retrieved relevant passages from the book:
{context}

Provide a clear, accurate answer based on the retrieved passages.
Cite specific concepts from the book.
If the passages don't fully answer the question, say so.

Answer:"""
        
        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant for Rich Dad Poor Dad."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=400
        )
        
        answer = response.choices[0].message.content
        
        # Add source information
        sources = "\n\n📚 **Sources:**\n"
        for i, item in enumerate(search_results[:3], 1):
            score = item.get('score', 0)
            sources += f"- Passage {i} (relevance: {score:.2f})\n"
        
        full_response = f"{answer}{sources}"
        
        logs.append({
            "agent": "search",
            "action": "Search complete",
            "timestamp": self._get_timestamp()
        })
        
        return full_response, logs
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
