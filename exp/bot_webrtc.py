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

# Optional imports for full features
try:
    from pipecat.services.deepgram import DeepgramSTTService
    STT_AVAILABLE = True
except:
    STT_AVAILABLE = False

try:
    from pipecat.transports.services.daily import DailyParams, DailyTransport
    DAILY_AVAILABLE = True
except:
    DAILY_AVAILABLE = False

try:
    from pipecat.vad.silero import SileroVADAnalyzer
    VAD_AVAILABLE = True
except:
    VAD_AVAILABLE = False

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
    print("🤖 ENDLESS NARRATOR BOT - Enhanced Version")
    print("=" * 60)
    
    # Check available features
    if DAILY_AVAILABLE:
        print("✅ Daily.co WebRTC transport available")
        mode = "webrtc"
    else:
        print("⚠️  Running in console mode (install daily-python for WebRTC)")
        mode = "console"
    
    if STT_AVAILABLE:
        print("✅ Speech-to-Text available (Deepgram)")
    else:
        print("💡 Install Deepgram for voice interruption: pip install deepgram-sdk")
    
    if VAD_AVAILABLE:
        print("✅ Voice Activity Detection available (Silero)")
    else:
        print("💡 Install Silero for better VAD: pip install silero")
    
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
        voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",   # British Lady
        model_id="sonic-english",
    )
    
    # Optional: Speech-to-Text for interruption
    stt = None
    if STT_AVAILABLE and os.getenv("DEEPGRAM_API_KEY"):
        stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        print("🎤 Voice interruption enabled")
    
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

    # ── Build Pipeline Based on Available Features ─────────────
    if mode == "webrtc" and DAILY_AVAILABLE:
        # Full WebRTC pipeline with Daily.co
        vad = SileroVADAnalyzer() if VAD_AVAILABLE else None
        
        transport = DailyTransport(
            os.getenv("DAILY_ROOM_URL"),
            os.getenv("DAILY_TOKEN") if os.getenv("DAILY_TOKEN") else None,
            "Endless Narrator Bot",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_enabled=True if vad else False,
                vad_analyzer=vad,
                vad_audio_passthrough=True,
            )
        )
        
        # Build pipeline with transport
        pipeline_processors = [transport.input()]
        
        if stt:
            pipeline_processors.append(stt)
        
        pipeline_processors.extend([
            user_aggregator,
            llm,
            text_printer,
            tts,
            transport.output(),
            assistant_aggregator,
        ])
        
        pipeline = Pipeline(pipeline_processors)
        task = PipelineTask(pipeline)
        
        # Start narration when participant joins
        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            print(f"\n🎙️  Participant joined: {participant['id']}")
            print("🚀 Starting endless narration...\n")
            await task.queue_frames([LLMMessagesFrame(messages)])
        
        @transport.event_handler("on_participant_left")
        async def on_participant_left(transport, participant, reason):
            print(f"\n👋 Participant left: {participant['id']}")
            await task.queue_frames([EndFrame()])
        
        print(f"📍 Room: {os.getenv('DAILY_ROOM_URL')}")
        print("⏳ Waiting for participants to join...")
        print("💡 Open the room URL in your browser to hear the bot")
        print("=" * 60)
        print()
        
    else:
        # Console mode pipeline (simpler)
        pipeline = Pipeline([
            llm,
            text_printer,
            tts,
            assistant_aggregator,
        ])
        
        task = PipelineTask(pipeline)
        
        print("🎤 Bot will generate endless narration")
        print("💡 Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        # Start narration immediately
        await task.queue_frames([LLMMessagesFrame(messages)])
    
    # ── Run the bot ─────────────────────────────────────────────
    runner = PipelineRunner()
    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
