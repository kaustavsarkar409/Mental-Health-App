from dotenv import load_dotenv
load_dotenv()
import sys
import os
from gtts import gTTS


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crew import MentalHealthApp
def text_to_audio(text):
    print("DEBUG: Inside TTS function") 
    tts = gTTS(text)
    tts.save("support.mp3")

def run():
    print("\n--- Mental Health Assistant ---\n")

    user_input = input("Describe how you are feeling:\n")

    inputs = {
        "user_input": user_input
    }

    result = MentalHealthApp().crew().kickoff(inputs=inputs)

    print("\n✔ Analysis complete")
    print("🎧 Generating voice message...\n")

    clean_text = str(result)\
        .replace("Section 1:", "")\
        .replace("Section 2:", "")\
        .replace("Section 3:", "")\
        .replace("Section 4:", "")

    print("DEBUG: About to generate audio...")

    text_to_audio(clean_text)

    print("✅ Saved as support.mp3")

if __name__ == "__main__":
    run()