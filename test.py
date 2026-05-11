"""from utils.audio_processor import process_input
from core.transcriber import transcribe_all

source ="https://youtu.be/Lg-meK5IU8Q?si=7GEcTdpmLAB4vJ5U"

chunks = process_input(source)

print(transcribe_all(chunks))"""

from dotenv import load_dotenv
load_dotenv()
from utils.audio_processor import process_input
from core.transcriber import transcribe_all

load_dotenv()

source = "https://youtu.be/vFP1mgZ_LEY?si=w17sICYgTXetzubI"
language = "hinglish"

chunks = process_input(source)
transcript = transcribe_all(chunks, language=language)

print("\=== TRANSCRIPT ===\n")
print(transcript)