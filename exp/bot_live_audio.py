import os
import asyncio
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np

from pipecat.frames.frames import LLMMessagesFrame, AudioRawFrame
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


class TextPrinter(FrameProcessor):
    """Prints text frames to console"""
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        from pipecat.frames.frames import TextFrame
        if isinstance(frame, TextFrame):
            print(frame.text, end="", flush=True)
        
        await self.push_frame(frame, direction)


class AudioPlayer(FrameProcessor):
    """Plays audio frames in real-time through speakers"""
    def __init__(self):
        super().__init__()
        self.stream = None
        self.sample_rate = None  # Will be set from first audio frame
        
    async def start(self, frame):
        await super().start(frame)
        print("Audio player initialized - waiting for audio...\n")
    
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, AudioRawFrame):
            # Initialize stream with correct sample rate from audio frame
            if self.stream is None:
                self.sample_rate = frame.sample_rate
                try:
                    self.stream = sd.OutputStream(
                        channels=frame.num_channels,
                        samplerate=self.sample_rate,
                        dtype=np.int16
                    )
                    self.stream.start()
                    print(f"Playing audio at {self.sample_rate} Hz, {frame.num_channels} channel(s)\n")
                except Exception as e:
                    print(f"WARNING: Could not start audio: {e}\n")
            
            if self.stream:
                try:
                    # Convert bytes to numpy array and play
                    audio_data = np.frombuffer(frame.audio, dtype=np.int16)
                    self.stream.write(audio_data)
                except Exception as e:
                    print(f"WARNING: Audio playback error: {e}")
        
        await self.push_frame(frame, direction)
    
    async def stop(self, frame):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        await super().stop(frame)


async def main():
    print("=" * 60)
    print("ENDLESS NARRATOR BOT - LOCAL AUDIO PLAYBACK")
    print("=" * 60)
    print("Audio will play through your speakers automatically")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # ── Services ────────────────────────────────────────────────
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
    )

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",   # British Lady
        model_id="sonic-english",
    )
    
    text_printer = TextPrinter()
    audio_player = AudioPlayer()

    # ── Conversation context ───────────────────────────────────
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

    # ── Pipeline with Audio Playback ───────────────────────────
    pipeline = Pipeline([
        llm,
        text_printer,
        tts,
        audio_player,      # This plays the audio!
        assistant_aggregator,
    ])

    task = PipelineTask(pipeline)
    
    print("Starting endless narration with LIVE AUDIO...")
    print()
    
    # Start narration immediately
    await task.queue_frames([LLMMessagesFrame(messages)])
    
    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
