"""
Script to list available Cartesia voices
Run: python list_voices.py
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def list_voices():
    try:
        from cartesia import AsyncCartesia
        
        api_key = os.getenv("CARTESIA_API_KEY")
        if not api_key:
            print("❌ CARTESIA_API_KEY not found in .env file")
            return
        
        print("=" * 60)
        print("🎤 Available Cartesia Voices")
        print("=" * 60)
        print()
        
        client = AsyncCartesia(api_key=api_key)
        voices = await client.voices.list()
        
        # Convert to list
        voice_list = []
        async for voice in voices:
            voice_list.append(voice)
        
        print(f"Found {len(voice_list)} voices:\n")
        
        for i, voice in enumerate(voice_list, 1):
            # Handle both dict and object formats
            if isinstance(voice, dict):
                name = voice.get('name', 'Unknown')
                vid = voice.get('id', 'N/A')
                lang = voice.get('language', 'N/A')
                desc = voice.get('description', 'N/A')
            else:
                name = getattr(voice, 'name', 'Unknown')
                vid = getattr(voice, 'id', 'N/A')
                lang = getattr(voice, 'language', 'N/A')
                desc = getattr(voice, 'description', 'N/A')
            
            print(f"{i}. {name}")
            print(f"   ID: {vid}")
            print(f"   Language: {lang}")
            print(f"   Description: {desc}")
            print()
        
        print("=" * 60)
        print("💡 Copy a voice ID to use in bot.py")
        print("=" * 60)
        
    except ImportError:
        print("❌ Cartesia not installed. Run: pip install cartesia")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_voices())
