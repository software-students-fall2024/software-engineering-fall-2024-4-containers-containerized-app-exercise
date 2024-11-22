"""
File for generating a basic audio file.
"""

from gtts import gTTS

def main():
    """Generate a basic audio file with speech."""
    text = "This is a test audio file generated for the speech recognition system."
    output_file = "real_speech.wav"

    print("Generating a test audio file with speech using gTTS...")
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)
    print(f"Audio file generated: {output_file}")

if __name__ == "__main__":
    main()
