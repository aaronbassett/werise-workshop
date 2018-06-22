from tinydb import TinyDB, where
from .recording import download_recording
from .services import convert_speech_to_text, understand_transcript
from .celery import app


@app.task
def understand_recording(recording_url, recording_uuid):
    db = TinyDB("db.json")

    audio = download_recording(recording_url, recording_uuid)
    transcription = convert_speech_to_text(audio)
    analysis = understand_transcript(transcription)

    db.update(
        {
            "transcription": transcription["results"][0]["alternatives"][0][
                "transcript"
            ],
            "language": analysis["language"],
            "sentiment": analysis["sentiment"]["document"],
            "emotions": analysis["emotion"]["document"]["emotion"],
            "keywords": analysis["keywords"],
            "concepts": analysis["concepts"],
            "categories": analysis["categories"],
        },
        where("recording_uuid") == recording_uuid,
    )
