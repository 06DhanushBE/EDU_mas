#!/usr/bin/env python3
"""
Interactive Narrator Bot - Text Chat Version
- Narrates continuously
- You can type questions anytime
- Bot stops, answers, then resumes narration
"""

import os
import asyncio
import threading
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
from queue import Queue

from pipecat.frames.frames import LLMMessagesFrame, AudioRawFrame, TextFrame, UserStartedSpeakingFrame, UserStoppedSpeakingFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMUserResponseAggregator,
    LLMAssistantResponseAggregator
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.cartesia.tts import CartesiaTTSService

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


class AudioPlayer(FrameProcessor):
    """Plays audio frames in real-time through speakers"""
    def __init__(self):
        super().__init__()
        self.stream = None
        self.sample_rate = None
        
    async def start(self, frame):
        await super().start(frame)
    
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, AudioRawFrame):
            if self.stream is None:
                self.sample_rate = frame.sample_rate
                try:
                    self.stream = sd.OutputStream(
                        channels=frame.num_channels,
                        samplerate=self.sample_rate,
                        dtype=np.int16
                    )
                    self.stream.start()
                except Exception as e:
                    print(f"WARNING: Audio error: {e}")
            
            if self.stream:
                try:
                    audio_data = np.frombuffer(frame.audio, dtype=np.int16)
                    self.stream.write(audio_data)
                except Exception as e:
                    pass
        
        await self.push_frame(frame, direction)
    
    async def stop(self, frame):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        await super().stop(frame)


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
    print("INTERACTIVE NARRATOR BOT - Text Chat")
    print("=" * 60)
    print("Bot will narrate continuously")
    print("You can type questions anytime to interrupt")
    print("=" * 60)
    
    # Start input thread
    input_t = threading.Thread(target=input_thread, daemon=True)
    input_t.start()
    
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
    audio_player = AudioPlayer()
    
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
    
    # Create pipeline
    pipeline = Pipeline([
        llm,
        text_printer,
        tts,
        audio_player,
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
            await asyncio.sleep(0.05)  # Check more frequently
            
            # Check for user input
            if not user_input_queue.empty():
                user_question = user_input_queue.get()
                
                print(f"\n\n{'='*60}")
                print(f"INTERRUPTING...")
                print(f"YOU: {user_question}")
                print(f"{'='*60}\n")
                print("BOT: ", end="", flush=True)
                
                # Send interruption frames to stop current generation
                await task.queue_frames([
                    UserStartedSpeakingFrame(),
                    UserStoppedSpeakingFrame(),
                ])
                
                # Wait a moment for interruption to process
                await asyncio.sleep(0.2)
                
                # Add user message to conversation
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
