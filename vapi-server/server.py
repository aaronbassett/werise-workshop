import os
import time
import uuid
import jwt
import requests
import hug


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


@hug.post("/recordings", versions=1)
def recordings(recording_url, recording_uuid):
    iat = int(time.time())

    with open("private.key", "rb") as key_file:
        private_key = key_file.read()

    payload = {
        "application_id": os.environ["APPLICATION_ID"],
        "iat": iat,
        "exp": iat + 60,
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")

    recording_response = requests.get(
        recording_url,
        headers={"Authorization": b"Bearer " + token, "User-Agent": "voice-journal"},
    )
    if recording_response.status_code == 200:
        recordingfile = f"./recordings/{recording_uuid}.mp3"
        os.makedirs(os.path.dirname(recordingfile), exist_ok=True)

        with open(recordingfile, "wb") as f:
            f.write(recording_response.content)

    return {}


hug.API(__name__).http.serve(port=8800)
