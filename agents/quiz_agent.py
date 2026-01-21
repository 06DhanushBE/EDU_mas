"""
Quiz Agent - Generates questions from Qdrant-retrieved content
"""

import os
from typing import Tuple, List, Dict
from groq import Groq
from utils.qdrant_client import QdrantManager
import random


class QuizAgent:
    """
    Specialized agent for generating quizzes.
    Retrieves context from Qdrant and generates questions.
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.qdrant = QdrantManager()
    
    def generate_quiz(self, query: str) -> Tuple[str, List[Dict]]:
        """Generate quiz questions based on book content"""
        logs = []
        
        logs.append({
            "agent": "quiz",
            "action": "Preparing quiz generation",
            "timestamp": self._get_timestamp()
        })
        
        # Select random topics from the book
        topics = [
            "assets and liabilities",
            "financial literacy",
            "working for money vs money working for you",
            "corporation and taxes",
            "overcoming fear and obstacles"
        ]
        
        selected_topic = random.choice(topics)
        
        # Retrieve relevant content
        logs.append({
            "agent": "quiz",
            "action": f"Retrieving content about: {selected_topic}",
            "qdrant_query": selected_topic,
            "timestamp": self._get_timestamp()
        })
        
        retrieved_content = self.qdrant.search(selected_topic, limit=3)
        
        logs.append({
            "agent": "quiz",
            "action": f"Retrieved {len(retrieved_content)} passages",
            "timestamp": self._get_timestamp()
        })
        
        # Generate quiz
        logs.append({
            "agent": "quiz",
            "action": "Generating quiz with Groq LLM",
            "timestamp": self._get_timestamp()
        })
        
        context = "\n\n".join([item["text"] for item in retrieved_content])
        
        prompt = f"""You are creating a quiz about "Rich Dad Poor Dad" by Robert Kiyosaki.

Topic: {selected_topic}

Book content:
{context}

Generate 3 multiple-choice questions based on this content.
For each question:
1. Make it thought-provoking and educational
2. Provide 4 options (A, B, C, D)
3. Indicate the correct answer
4. Briefly explain why it's correct

Format:
**Question 1:** [question]
A) [option]
B) [option]
C) [option]
D) [option]

✓ **Answer:** [letter] - [brief explanation]

Quiz:"""
        
        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a quiz creator for Rich Dad Poor Dad."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=600
        )
        
        quiz = response.choices[0].message.content
        
        full_response = f"📝 **Quiz Time!** (Topic: {selected_topic})\n\n{quiz}\n\n*Take your time and think through each answer!*"
        
        logs.append({
            "agent": "quiz",
            "action": "Quiz generated successfully",
            "timestamp": self._get_timestamp()
        })
        
        return full_response, logs
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
