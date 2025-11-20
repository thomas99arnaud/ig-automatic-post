from openai import OpenAI
import re

client = OpenAI()

from openai import OpenAI

client = OpenAI()

def get_timings_from_audio(audio_path):
    with open(audio_path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            language="fr",
        )

    segments = tr.segments  # objets TranscriptionSegment

    timings = []
    for seg in segments:
        # seg.text est le texte de ce bout d'audio
        # seg.start / seg.end sont les timings en secondes
        timings.append((
            seg.text.strip(),
            seg.start,
            seg.end,
        ))

    return timings
