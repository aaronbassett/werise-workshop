import os
import hug
from tinydb import TinyDB, where
from understanding.tasks import understand_recording


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
def recordings(conversation_uuid, recording_url, recording_uuid, start_time, end_time):

    db = TinyDB("db.json")

    entry_meta = {
        "conversation_uuid": conversation_uuid,
        "recording_url": recording_url,
        "recording_uuid": recording_uuid,
        "start_time": start_time,
        "end_time": end_time,
    }

    if db.contains(where("conversation_uuid") == conversation_uuid):
        db.update(entry_meta, where("conversation_uuid") == conversation_uuid)
    else:
        db.insert(entry_meta)

    understand_recording.delay(recording_url, recording_uuid)

    return {}


hug.API(__name__).http.serve(port=8800)
