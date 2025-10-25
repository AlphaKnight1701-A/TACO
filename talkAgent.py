import os
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# --- ElevenLabs Imports (from the new examples) ---
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

# --- Audio Recording Imports ---
import sounddevice as sd
import soundfile as sf
MIC_DEVICE_ID = 2
# --- Load Environment Variables ---
load_dotenv()

# --- 1. Configure Gemini ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("X GOOGLE_API_KEY not found in .env")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# --- 2. Configure ElevenLabs Client ---
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVEN_API_KEY:
    raise RuntimeError("X - ELEVENLABS_API_KEY not found in .env")

# This is the correct way to initialize the client, as per your examples
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)

# Use the default "Adam" voice ID as requested
DEFAULT_VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"

# --- 3. Audio Utility Functions (Moved from utils.py) ---

# --- 3. Audio Utility Functions (Moved from utils.py) ---

def record_audio(filename="input.wav", duration=5, samplerate=44100, device_id=None):
    """
    Record microphone audio for a duration and save to WAV.
    
    :param filename: The name of the file to save the recording to.
    :param duration: The duration in seconds to record.
    :param samplerate: The sample rate for the recording.
    :param device_id: The ID of the input device to use (e.g., 0, 1, etc.).
    """
    # Use the provided device_id, which can be None to use the system default
    device_info = f"Device ID: {device_id}" if device_id is not None else "Default Device"
    print(f"🎤 Recording audio for {duration} seconds using {device_info}...")
    
    # Record audio
    # Pass the device_id to the 'device' argument of sd.rec()
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, 
                   dtype='int16', device=device_id) 
    sd.wait()  # Wait for recording to complete
    
    # Save to file
    sf.write(filename, audio, samplerate)
    print(f"✅ Audio saved to {filename}")
    return filename

# ... (rest of the script)

def speak_text(text: str, voice_id: str = DEFAULT_VOICE_ID):
    """
    Convert text to speech using ElevenLabs TTS and play it.
    Uses the method from your 'text to speech' example.
    """
    print(" Generating speech...")
    try:
        # Use the correct TTS method from your example
        audio_bytes = eleven_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128"
        )
        
        print(" Playing response...")
        # --- FIX 2: Added error handling for playback ---
        # This stops the program from crashing if ffmpeg is not installed
        try:
            play(audio_bytes)
        except Exception as e_play:
            print(f"fix ffmpeg: {e_play}")
        
    except Exception as e_tts:
        print(f"tts API call fail: {e_tts}")

# --- 4. Core Application Logic ---

async def transcribe_audio_realtime(filename: str) -> str:
    """
    Transcribe recorded audio using ElevenLabs STT API.
    Uses the method from your 'example.py' (STT) example.
    """
    print("translating audio...")
    try:
        with open(filename, "rb") as audio_file:
            # --- FIX 1: Corrected the STT model_id ---
            # The API error said 'eleven_multilingual_stt_v2' was invalid
            # and that only 'scribe_v1' or 'scribe_v1_experimental' are available.
            transcript = eleven_client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1" 
            )
        
        # The response object has a 'text' attribute
        text = transcript.text.strip() if hasattr(transcript, 'text') else ""
        
        print(f"🗣️ Transcription: {text}")
        return text
        
    except Exception as e:
        print(f"couldnt translate: {e}")
        return ""

async def interpret_command():
    """Main loop: listen -> transcribe -> interpret -> respond"""
    
    print("agents started. Speak a command or 'exit' to quit.")
    speak_text("Yo whats up dawg! Its me taco what do you want me to do?")

    while True:
        # 1. Record audio from the user
        filename = record_audio(duration=5, device_id=MIC_DEVICE_ID)        
        # 2. Transcribe audio to text
        user_text = await transcribe_audio_realtime(filename)

        if not user_text:
            print("No speech detected.")
            continue

        # 3. Check for exit condition immediately after transcription
        if "exit" in user_text.lower() or "quit" in user_text.lower():
            print("👋 Exiting agent.")
            speak_text("Goodbye, keep it funny out there!")
            break

        # 4. Send text to Gemini for command interpretation
        prompt = f"""
        You are a command-understanding and conversational AI named Taco. 
        Convert the following user speech into a JSON object that includes both a list of commands and a funny, short, conversational reply.

        The JSON must have two top-level keys:
        1. 'response_text': A funny, engaging, short and conversational reply to the user.
        2. 'commands': An array of command objects.

        Example:
        User: "Can you move the ball from there to the left a bit"
        Output: {{
            "response_text": "You got it, little ball! Here I come to scoot you to the left!",
            "commands": [
                {{"action": "move", "object": "sports ball", "direction": "left", "amount": "a bit"}}
            ]
        }}
        
        The only valid objects for the 'object' key in your command are listed below. If the user mentions an object that is NOT on this list (e.g., 'little ball'), you MUST choose the closest matching object from the list to use in the command (e.g., 'sports ball').

        Valid Object List (comma-separated):
        person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

        Now for this user input:
        "{user_text}"
        """
        
        print("Thinking...")
        # --- START OF REVISED LOGIC ---
        
        commands = None # Will hold the parsed JSON object
        response_to_speak = "I understood that, but I need a moment to translate it into a witty response." # Default fallback reply

        try:
            response = model.generate_content(prompt)
            text_response = response.text

            # Parse Gemini's JSON response
            try:
                # 5a. Isolate the JSON string (in case Gemini adds prose outside the curly braces)
                start = text_response.find("{")
                end = text_response.rfind("}") + 1
                json_str = text_response[start:end]
                
                # 5b. Load the JSON and extract the speech part
                parsed_json = json.loads(json_str)
                commands = parsed_json # Store the full JSON for terminal output
                
                # CRITICAL: ONLY extract the 'response_text' for speaking
                response_to_speak = commands.get("response_text", f"I heard '{user_text}', but my funny bone is on vacation.")

            except Exception as e_json:
                print(f"Could not parse JSON ({e_json}). Falling back to raw text command.")
                # If parsing fails, create a simple JSON structure for logging/terminal output
                commands = {
                    "response_text": response_to_speak,
                    "commands": [{"raw_text": user_text, "error": "JSON_PARSE_FAILURE"}]
                }
            
            # 6. Terminal output: show the full JSON, even if it's the fallback version
            print("📦 Command JSON:", json.dumps(commands, indent=2))
            
            # 7. Respond with the funny voice reply (which is now guaranteed to be a string)
            speak_text(response_to_speak)
                
        except Exception as e_gemini:
            print(f"Gemini call failed: {e_gemini}")
            speak_text("Sorry, a connection error stopped me from understanding that.")

if __name__ == "__main__":
    asyncio.run(interpret_command())


