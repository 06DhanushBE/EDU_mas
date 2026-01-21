import os
import asyncio
from dotenv import load_dotenv

from pipecat.frames.frames import LLMMessagesFrame, EndFrame, TextFrame
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
    """Simple processor that prints text frames to console"""
    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            print(frame.text, end="", flush=True)
        
        await self.push_frame(frame, direction)

async def main():
    print("=" * 60)
    print("🤖 ENDLESS NARRATOR BOT")
    print("=" * 60)
    print("⚠️  Running in console mode (text + audio generation)")
    print("💡 To use with WebRTC/Daily.co, run: pip install daily-python")
    print()
    
    # ── Services ────────────────────────────────────────────────
    # Groq LLM - ultra-fast inference
    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",   # fast & intelligent
    )

    # Cartesia TTS - ultra-low latency streaming speech  
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",   # British Lady - clear, natural voice
        # Other popular voices:
        # "248be419-c632-4f23-adf1-5324ed7dbf1d" - Conversational Man
        # "79a125e8-cd45-4c13-8a67-188112f4dd22" - British Lady  
        # "156fb8d2-335b-4950-9cb3-a2d33befec77" - Classy British Man
        model_id="sonic-english",   # fastest model
    )
    
    # Text printer to see the narration
    text_printer = TextPrinter()

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

    # Aggregators to collect user and assistant messages
    user_aggregator = LLMUserResponseAggregator(messages)
    assistant_aggregator = LLMAssistantResponseAggregator(messages)

    # ── The Pipeline ────────────────────────────────────────────
    # Simple pipeline: LLM -> TTS
    pipeline = Pipeline([
        llm,                        # generate continuous narration
        text_printer,               # print text to console
        tts,                        # convert to speech (streaming)
        assistant_aggregator,       # save assistant responses
    ])

    # ── Task & Initial Trigger ──────────────────────────────────
    task = PipelineTask(pipeline)

    # ── Run the bot ─────────────────────────────────────────────
    runner = PipelineRunner()
    
    print("🎤 Bot will generate endless narration")
    print("💡 Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Start narration immediately
    await task.queue_frames([LLMMessagesFrame(messages)])
    
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
