import os
import hug


@hug.get("/ncco", versions=1)
def echo():
    return [
        {"action": "talk", "text": "Record your message after the beep"},
        {
            "action": "record",
            "eventUrl": [f"{os.environ['VAPI_SERVER_URL']}/recordings"],
            "endOnKey": "*",
            "beepStart": True,
        },
    ]
