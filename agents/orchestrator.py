"""
Orchestrator Agent - Routes user queries to appropriate specialized agents
"""

import re
from typing import Tuple, List, Dict
from agents.tutor_agent import TutorAgent
from agents.search_agent import SearchAgent
from agents.quiz_agent import QuizAgent


class OrchestratorAgent:
    """
    Master agent that analyzes user intent and routes to specialized agents.
    Implements multi-agent coordination pattern.
    """
    
    def __init__(self):
        self.tutor = TutorAgent()
        self.search = SearchAgent()
        self.quiz = QuizAgent()
        self.conversation_context = []
    
    def process(self, user_query: str) -> Tuple[str, List[Dict]]:
        """
        Main processing method - analyzes intent and routes to appropriate agent
        
        Returns:
            Tuple of (response_text, agent_logs)
        """
        logs = []
        
        # Log orchestrator activity
        logs.append({
            "agent": "orchestrator",
            "action": f"Analyzing query: {user_query[:50]}...",
            "timestamp": self._get_timestamp()
        })
        
        # Intent classification
        intent = self._classify_intent(user_query)
        
        logs.append({
            "agent": "orchestrator",
            "action": f"Classified intent: {intent}",
            "timestamp": self._get_timestamp()
        })
        
        # Route to appropriate agent
        if intent == "teach":
            logs.append({
                "agent": "orchestrator",
                "action": "Routing to Tutor Agent",
                "timestamp": self._get_timestamp()
            })
            response, agent_logs = self.tutor.teach(user_query)
            logs.extend(agent_logs)
            
        elif intent == "search":
            logs.append({
                "agent": "orchestrator",
                "action": "Routing to Search Agent",
                "timestamp": self._get_timestamp()
            })
            response, agent_logs = self.search.semantic_search(user_query)
            logs.extend(agent_logs)
            
        elif intent == "quiz":
            logs.append({
                "agent": "orchestrator",
                "action": "Routing to Quiz Agent",
                "timestamp": self._get_timestamp()
            })
            response, agent_logs = self.quiz.generate_quiz(user_query)
            logs.extend(agent_logs)
            
        else:
            # Default to search for general questions
            logs.append({
                "agent": "orchestrator",
                "action": "Default routing to Search Agent",
                "timestamp": self._get_timestamp()
            })
            response, agent_logs = self.search.semantic_search(user_query)
            logs.extend(agent_logs)
        
        return response, logs
    
    def _classify_intent(self, query: str) -> str:
        """Classify user intent based on query patterns"""
        query_lower = query.lower()
        
        # Teaching intent keywords
        teach_keywords = [
            "teach", "explain", "lesson", "start", "begin", "chapter",
            "tell me about", "walk me through", "introduce", "overview"
        ]
        
        # Search intent keywords
        search_keywords = [
            "what", "how", "why", "when", "where", "find", "search",
            "does the book say", "according to", "mentions"
        ]
        
        # Quiz intent keywords
        quiz_keywords = [
            "quiz", "test", "question", "assess", "check my",
            "evaluate", "challenge", "exercise"
        ]
        
        # Check quiz first (most specific)
        if any(keyword in query_lower for keyword in quiz_keywords):
            return "quiz"
        
        # Then teaching
        if any(keyword in query_lower for keyword in teach_keywords):
            return "teach"
        
        # Then search
        if any(keyword in query_lower for keyword in search_keywords):
            return "search"
        
        # Default to search
        return "search"
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
