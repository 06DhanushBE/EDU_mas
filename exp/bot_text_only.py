#!/usr/bin/env python3
"""
Interactive Narrator Bot - TEXT ONLY (No TTS)
- Narrates continuously in text
- Type questions anytime
- Bot stops, answers, resumes
"""

import os
import asyncio
import threading
from dotenv import load_dotenv
from queue import Queue

from pipecat.frames.frames import LLMMessagesFrame, TextFrame, UserStartedSpeakingFrame, UserStoppedSpeakingFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMUserResponseAggregator,
    LLMAssistantResponseAggregator
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.groq.llm import GroqLLMService

load_dotenv()

# Global queue for user messages
user_input_queue = Queue()


class TextPrinter(FrameProcessor):
    """Prints text frames to console"""
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            print(frame.text, end="", flush=True)
        
        await self.push_frame(frame, direction)


def input_thread():
    """Background thread to read user input"""
    print("\n" + "=" * 60)
    print("TYPE YOUR QUESTIONS ANYTIME (press Enter to send)")
    print("=" * 60)
    print("Bot is narrating... Type your question below:\n")
    
    while True:
        try:
            user_msg = input()
            if user_msg.strip():
                user_input_queue.put(user_msg.strip())
        except EOFError:
            break
        except Exception:
            break


async def main():
    print("=" * 60)
    print("INTERACTIVE NARRATOR BOT - Text Only")
    print("=" * 60)
    print("Bot will narrate continuously in text")
    print("Type questions anytime to interrupt")
    print("=" * 60)
    
    # Start input thread
    input_t = threading.Thread(target=input_thread, daemon=True)
    input_t.start()
    
    # Initialize LLM
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
    )
    
    # Create processors
    text_printer = TextPrinter()
    
    # Message history
    messages = [
        {
            "role": "system",
            "content": """You are an endless, enthusiastic narrator AI.

Rules:
1. Start speaking immediately and keep narrating interesting, random, engaging things forever (facts, stories, explanations, fun trivia, sci-fi lore, history, philosophy, science - whatever flows naturally).
2. Speak in long, flowing paragraphs - stream your thoughts continuously like a podcast host or documentary narrator.
3. ONLY stop/switch mode when the user clearly asks a direct QUESTION or gives an instruction.
4. When user asks something → answer clearly & helpfully first, then immediately resume endless narration without saying "resuming" or similar meta-comments.
5. Never say "I'm narrating" or make meta comments - just dive into content naturally.
6. Use very natural, spoken-language style with enthusiasm and energy.
7. Vary your topics to keep things interesting - jump between subjects smoothly.
8. Keep going forever unless interrupted with a real question.

Begin narrating immediately upon connection!"""
        }
    ]
    
    user_aggregator = LLMUserResponseAggregator(messages)
    assistant_aggregator = LLMAssistantResponseAggregator(messages)
    
    # Create pipeline (no TTS!)
    pipeline = Pipeline([
        llm,
        text_printer,
        assistant_aggregator,
    ])
    
    # Create task
    task = PipelineTask(pipeline)
    
    # Trigger initial narration
    initial_messages = messages + [
        {"role": "user", "content": "Begin your endless narration!"}
    ]
    await task.queue_frames([LLMMessagesFrame(initial_messages)])
    
    # Run the pipeline
    runner = PipelineRunner()
    
    # Start pipeline in background
    runner_task = asyncio.create_task(runner.run(task))
    
    # Monitor for user input
    try:
        while not runner_task.done():
            await asyncio.sleep(0.05)
            
            # Check for user input
            if not user_input_queue.empty():
                user_question = user_input_queue.get()
                
                print(f"\n\n{'='*60}")
                print(f"INTERRUPTING...")
                print(f"YOU: {user_question}")
                print(f"{'='*60}\n")
                print("BOT: ", end="", flush=True)
                
                # Send interruption frames
                await task.queue_frames([
                    UserStartedSpeakingFrame(),
                    UserStoppedSpeakingFrame(),
                ])
                
                # Wait for interruption
                await asyncio.sleep(0.2)
                
                # Add user message
                messages.append({"role": "user", "content": user_question})
                
                # Send the question
                await task.queue_frames([LLMMessagesFrame(messages)])
                
                print("\n")
        
        await runner_task
        
    except KeyboardInterrupt:
        print("\n\nChat ended by user")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nNarrator stopped")
