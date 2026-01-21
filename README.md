# Multi-Agent AI Tutoring System

## Hackathon Submission - MAS Track at Convolve 4.0

A multi-agent system for teaching concepts from any PDF document using Qdrant vector database and Groq LLM. The system processes PDF files, extracts content, and provides interactive tutoring through specialized agents.

## Multi-Agent Architecture

### System Design

```
User Query
    ↓
┌─────────────────────┐
│ Orchestrator Agent  │ ← Master coordinator
└─────────────────────┘
         ↓
    [Routes to]
         ↓
    ┌────┴────┬────────┬────────┐
    ↓         ↓        ↓        ↓
┌─────┐  ┌──────┐  ┌──────┐  ┌──────┐
│Tutor│  │Search│  │ Quiz │  │Future│
│Agent│  │Agent │  │Agent │  │Agents│
└─────┘  └──────┘  └──────┘  └──────┘
    ↓         ↓        ↓
  [Qdrant Vector Database]
    ↓         ↓        ↓
  [Groq LLM Generation]
```

### Agent Responsibilities

| Agent            | Purpose                                 | Qdrant Usage              | LLM Role              |
| ---------------- | --------------------------------------- | ------------------------- | --------------------- |
| **Orchestrator** | Routes queries based on intent analysis | No direct access          | Intent classification |
| **Tutor**        | Sequential teaching, lesson progression | Retrieves chapter content | Explains concepts     |
| **Search**       | Semantic search across book             | Vector similarity search  | Synthesizes answers   |
| **Quiz**         | Generates assessment questions          | Retrieves topic content   | Creates questions     |

## Key Features

- **Multi-Agent System**: 4 specialized agents with clear separation of concerns
- **Qdrant Integration**: Vector search for semantic retrieval
- **Sequential Teaching**: Progressive lesson delivery with tracking
- **Interactive Q&A**: Semantic search for specific questions
- **Automated Quizzes**: Context-aware question generation
- **Real-time Monitoring**: Agent activity logs and Qdrant query tracking

## Quick Start

### Prerequisites

```bash
Python 3.8+
Qdrant Cloud Account
Groq API Key
```

### Installation

```bash
# Clone repository
cd "last MAS"

# Install dependencies
pip install streamlit groq qdrant-client python-dotenv

# Configure environment
# Create .env file with:
# GROQ_API_KEY=your_key
# QDRANT_URL=your_url
# QDRANT_API_KEY=your_key
```

### Run Demo

```bash
# Run the main voice agent
python pipecat_voice_agent.py

# Or explore experimental features
python exp/bot_interactive.py
```

### PDF Processing

The system includes a PDF processor in the Jupyter notebook that:
- Extracts text from PDF documents
- Chunks content into semantic passages
- Generates embeddings for vector search
- Stores in Qdrant collections for retrieval

## System Workflow

### Example 1: Teaching Flow

```
User: "Start teaching me from the document"
    ↓
Orchestrator: Analyzes → Intent = "teach"
    ↓
Tutor Agent: Activated
    ↓
Qdrant: Retrieves sequential content vectors
    ↓
Groq: Generates explanation from context
    ↓
User: Receives lesson + progress tracker
```

### Example 2: Search Flow

```
User: "Explain the main concepts in section X"
    ↓
Orchestrator: Analyzes → Intent = "search"
    ↓
Search Agent: Activated
    ↓
Qdrant: Vector similarity search across PDF content
    ↓
Groq: Synthesizes answer from top-k results
    ↓
User: Receives answer + source citations
```

### Example 3: Quiz Flow

```
User: "Test my understanding"
    ↓
Orchestrator: Analyzes → Intent = "quiz"
    ↓
Quiz Agent: Activated
    ↓
Qdrant: Retrieves random topic content
    ↓
Groq: Generates MCQ questions
    ↓
User: Receives quiz with explanations
```

## Technical Stack

- **Frontend**: Streamlit (Interactive UI)
- **Vector DB**: Qdrant (Semantic search)
- **LLM**: Groq (llama-3.1-70b-versatile)
- **Agent Framework**: Custom implementation
- **Language**: Python 3.11

## Project Structure

```
last MAS/
├── pipecat_voice_agent.py         # Main voice-enabled application
├── agents/                         # Agent modules
│   ├── __init__.py
│   ├── orchestrator.py            # Master routing agent
│   ├── tutor_agent.py             # Teaching specialist
│   ├── search_agent.py            # Semantic search specialist
│   └── quiz_agent.py              # Assessment specialist
├── utils/                          # Utility modules
│   ├── __init__.py
│   └── qdrant_client.py           # Qdrant operations
├── exp/                            # Experimental features
│   ├── bot_interactive.py         # Interactive bot variants
│   ├── bot_webrtc.py              # WebRTC implementation
│   └── ...                        # Other experimental features
├── hackathon_solution_clean.ipynb # Development notebook with PDF processor
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Educational Value

This system demonstrates:

1. **Multi-Agent Coordination**: Agents communicate through orchestrator
2. **Specialization**: Each agent handles specific tasks efficiently
3. **Qdrant Vector Search**: Semantic retrieval vs keyword matching
4. **Context-Aware Generation**: LLM uses retrieved context
5. **Scalable Architecture**: Easy to add new agents

## Innovation Highlights

### 1. Intent-Based Routing

Orchestrator classifies user intent using pattern matching and routes to appropriate agent.

### 2. Progressive Teaching

Tutor agent maintains lesson state and provides sequential content delivery.

### 3. Source Attribution

Search agent provides relevance scores and passage citations.

### 4. Dynamic Quiz Generation

Quiz agent selects random topics and generates contextual questions.

## Qdrant Usage

### Vector Storage

- Collections: PDF content, teaching styles, student memory, agent learning
- Vectors: Document passages extracted from uploaded PDFs
- Embedding: Semantic text representations using sentence transformers

### Search Operations

```python
# Semantic search example
results = qdrant.search(
    collection_name="pdf_content",
    query="your search query",
    limit=5
)
# Returns: Top-5 most relevant passages from uploaded PDF
```

## Performance Metrics

- **Response Time**: < 3 seconds per query
- **Search Accuracy**: Semantic relevance via vector similarity
- **Agent Coordination**: Real-time routing with logging
- **Scalability**: Modular design for additional agents

## Demo Scenarios

### Scenario 1: New Learner

```
1. User uploads PDF document
2. System processes and vectorizes content
3. User starts → "Begin teaching me"
4. Tutor agent activates → Retrieves sequential content
5. Progressive lessons → Knowledge assessment
```

### Scenario 2: Specific Question

```
1. User asks → "Explain concept X from the document"
2. Search agent activates → Qdrant semantic search
3. Answer with citations → Source attribution from PDF
```

### Scenario 3: Assessment

```
1. User requests → "Test me"
2. Quiz agent activates → Random topic selection
3. Questions generated → With explanations
```

## Future Enhancements

- [ ] Voice interaction (STT/TTS)
- [ ] Memory agent (conversation history)
- [ ] Visualization agent (concept diagrams)
- [ ] Multi-book support
- [ ] Collaborative learning (multi-user)

## Environment Variables

Required in `.env`:

```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Submission Checklist

- [x] Multi-agent system implementation
- [x] Qdrant as primary vector search
- [x] Clear agent separation
- [x] Interactive demo
- [x] Comprehensive documentation
- [x] Reproducible setup
- [x] Educational value

## Team Information

- **Track**: Multi-Agent Systems (MAS) - Qdrant
- **Event**: Convolve 4.0
- **Institution**: R V University, Bengaluru, Karnataka
- **Participant**: Dhanush B E

## Contact

For questions about this submission: dhanushbe106@gmail.com

---

Built for Convolve 4.0 | Powered by Qdrant and Groq
