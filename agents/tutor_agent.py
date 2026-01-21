"""
Tutor Agent - Sequential teaching with Qdrant-powered content retrieval
"""

import os
from typing import Tuple, List, Dict
from groq import Groq
from utils.qdrant_client import QdrantManager


class TutorAgent:
    """
    Specialized agent for sequential teaching.
    Uses Qdrant to retrieve relevant book sections and Groq for generation.
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.qdrant = QdrantManager()
        self.current_section = 0
        self.sections = [
            "Introduction and Background",
            "The Two Dads Philosophy",
            "Lesson 1: The Rich Don't Work for Money",
            "Lesson 2: Why Teach Financial Literacy",
            "Lesson 3: Mind Your Own Business",
            "Lesson 4: The History of Taxes and Power of Corporations",
            "Lesson 5: The Rich Invent Money",
            "Lesson 6: Work to Learn, Don't Work for Money",
            "Overcoming Obstacles",
            "Getting Started - Action Steps"
        ]
    
    def teach(self, query: str) -> Tuple[str, List[Dict]]:
        """Teach a section using Qdrant retrieval + Groq generation"""
        logs = []
        
        logs.append({
            "agent": "tutor",
            "action": "Preparing teaching content",
            "timestamp": self._get_timestamp()
        })
        
        # Determine which section to teach
        if "start" in query.lower() or "begin" in query.lower():
            self.current_section = 0
        
        section_name = self.sections[self.current_section]
        
        # Retrieve relevant content from Qdrant
        logs.append({
            "agent": "tutor",
            "action": f"Querying Qdrant for: {section_name}",
            "qdrant_query": section_name,
            "timestamp": self._get_timestamp()
        })
        
        retrieved_content = self.qdrant.search(section_name, limit=3)
        
        logs.append({
            "agent": "tutor",
            "action": f"Retrieved {len(retrieved_content)} relevant passages",
            "timestamp": self._get_timestamp()
        })
        
        # Generate teaching content
        logs.append({
            "agent": "tutor",
            "action": "Generating explanation with Groq LLM",
            "timestamp": self._get_timestamp()
        })
        
        context = "\n\n".join([item["text"] for item in retrieved_content])
        
        prompt = f"""You are a tutor teaching "Rich Dad Poor Dad" by Robert Kiyosaki.

Section: {section_name}

Retrieved book content:
{context}

User query: {query}

Provide a clear, engaging explanation of this section. Use the retrieved content as reference.
Be conversational and educational. Break down complex concepts simply.
End with a question to check understanding.

Response:"""
        
        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert tutor for Rich Dad Poor Dad."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        # Add section progress
        self.current_section = min(self.current_section + 1, len(self.sections) - 1)
        
        full_response = f"📖 **{section_name}**\n\n{answer}\n\n*Progress: Section {self.current_section}/{len(self.sections)}*"
        
        logs.append({
            "agent": "tutor",
            "action": "Teaching complete",
            "timestamp": self._get_timestamp()
        })
        
        return full_response, logs
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
