import os
import hug
from understanding.tasks import download_recording


@hug.get("/ncco", versions=1)
def echo():
    return [
        {"action": "talk", "text": "Record your message after the beep"},
        {
            "action": "record",
            "eventUrl": [f"{os.environ['VAPI_SERVER_URL']}/v1/recordings"],
            "endOnKey": "*",
            "beepStart": True,
        },
    ]


@hug.post("/events", versions=1)
def events(**kwargs):
    return kwargs


@hug.post("/recordings", versions=1)
def recordings(recording_url, recording_uuid):
    download_recording.delay(recording_url, recording_uuid)
    return {}


hug.API(__name__).http.serve(port=8800)
