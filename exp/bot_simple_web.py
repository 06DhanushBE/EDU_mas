#!/usr/bin/env python3

"""
Simple Web-Based Bot - Access via Browser (No Daily SDK)
Uses Pipecat's HTTP/WebSocket transport as an alternative to Daily.co
"""

import os
import asyncio
from dotenv import load_dotenv
from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.groq import GroqLLMService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator
from pipecat.frames.frames import LLMMessagesFrame

# Load environment variables
load_dotenv()

# Text printer processor (same as before)
class TextPrinter:
    def __init__(self):
        self._text_buffer = ""

    async def process_frame(self, frame, direction):
        from pipecat.frames.frames import TextFrame
        if isinstance(frame, TextFrame):
            print(frame.text, end="", flush=True)
            self._text_buffer += frame.text
        return frame

async def main():
    """
    ALTERNATIVE APPROACH: Run bot locally and access via simple HTTP server
    Since Daily.co SDK is unavailable, we'll document how to use ngrok or similar
    """
    
    logger.info("🎙️ Endless Narrator Bot - Web Access Mode")
    logger.info("=" * 60)
    logger.info("⚠️  Daily.co SDK not available - using local mode")
    logger.info("💡 To access via browser, you can:")
    logger.info("   1. Run this bot locally")
    logger.info("   2. Use 'ngrok http 8000' to expose it")
    logger.info("   3. Or use another WebRTC platform (Twilio, Agora)")
    logger.info("=" * 60)
    
    # Initialize services
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
    )
    
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
    )
    
    # Create processors
    text_printer = TextPrinter()
    assistant_aggregator = LLMAssistantResponseAggregator()
    
    # System prompt for endless narration
    system_prompt = """You are an endless, enthusiastic narrator AI who speaks continuously about anything fascinating.

RULES:
1. Never stop talking - seamlessly transition between topics
2. Talk about science, philosophy, history, nature, technology, mysteries
3. Use vivid descriptions and storytelling
4. Each response should be 3-5 sentences, then automatically continue
5. No questions asking "would you like to hear more?" - just keep going
6. Be energetic and captivating like a documentary narrator
7. Mix facts with wonder and curiosity
8. Flow naturally from one topic to another

Start narrating NOW about something amazing in the universe!"""
    
    # Create pipeline
    pipeline = Pipeline([
        llm,
        text_printer,
        tts,
        assistant_aggregator,
    ])
    
    # Create task
    task = PipelineTask(pipeline, PipelineParams())
    
    # Trigger initial narration
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Begin your endless narration!"}
    ]
    
    await task.queue_frames([LLMMessagesFrame(messages)])
    
    # Run the pipeline
    runner = PipelineRunner()
    
    logger.info("\n🎬 Starting endless narration...\n")
    logger.info("📝 Text will appear below:")
    logger.info("-" * 60 + "\n")
    
    await runner.run(task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Narration stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
