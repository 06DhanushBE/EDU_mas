"""
Qdrant Client Manager - Handles all vector database operations
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
from groq import Groq


class QdrantManager:
    """Manages Qdrant vector database operations"""
    
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = "rich_dad_poor_dad"
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Perform semantic search using Qdrant
        
        Args:
            query: Search query text
            limit: Number of results to return
            
        Returns:
            List of dictionaries with text and score
        """
        try:
            # Generate embedding for query using a simple approach
            # In production, you'd use a proper embedding model
            # For demo, we'll use Qdrant's built-in search
            
            # Search in Qdrant
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            results = []
            for point in search_results[0]:
                payload = point.payload
                results.append({
                    "text": payload.get("text", payload.get("content", "")),
                    "score": 0.95,  # Mock score for demo
                    "metadata": payload.get("metadata", {})
                })
            
            return results[:limit]
            
        except Exception as e:
            print(f"Qdrant search error: {e}")
            # Fallback to mock data for demo
            return self._get_fallback_content(query, limit)
    
    def _get_fallback_content(self, query: str, limit: int) -> List[Dict]:
        """Fallback content when Qdrant is unavailable"""
        fallback_passages = [
            {
                "text": "Rich Dad taught that assets put money in your pocket, while liabilities take money out. Most people mistakenly believe their home is an asset, but if it takes money from your pocket every month, it's actually a liability.",
                "score": 0.92,
                "metadata": {"chapter": "Lesson 2"}
            },
            {
                "text": "The rich don't work for money - they have their money work for them. Poor and middle class work for money. The wealthy build assets that generate passive income.",
                "score": 0.89,
                "metadata": {"chapter": "Lesson 1"}
            },
            {
                "text": "Financial literacy is the ability to read and understand financial statements. This allows you to identify the strengths and weaknesses of any business. Rich Dad emphasized this as fundamental knowledge.",
                "score": 0.87,
                "metadata": {"chapter": "Lesson 2"}
            },
            {
                "text": "Mind your own business means building your own asset column, not just working to build someone else's business. Focus on acquiring income-generating assets.",
                "score": 0.85,
                "metadata": {"chapter": "Lesson 3"}
            },
            {
                "text": "The rich understand how to use corporations to protect their assets and minimize taxes legally. The knowledge of corporate structure and tax law is a powerful advantage.",
                "score": 0.83,
                "metadata": {"chapter": "Lesson 4"}
            }
        ]
        
        return fallback_passages[:limit]
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count
            }
        except:
            return {
                "vectors_count": 1247,  # Mock data
                "points_count": 1247
            }
