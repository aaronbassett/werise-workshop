import os
from watson_developer_cloud import SpeechToTextV1, NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import (
    Features,
    EntitiesOptions,
    KeywordsOptions,
    CategoriesOptions,
    ConceptsOptions,
    EmotionOptions,
    SentimentOptions,
)


def convert_speech_to_text(audio):
    speech_to_text = SpeechToTextV1(
        username=os.environ["WATSON_TRANSCRIPTION_USERNAME"],
        password=os.environ["WATSON_TRANSCRIPTION_PASSWORD"],
    )

    return speech_to_text.recognize(
        audio, content_type="audio/mp3", timestamps=False, word_confidence=False
    )


def understand_transcript(transcription):
    nlp_client = NaturalLanguageUnderstandingV1(
        version="2017-02-27",
        username=os.environ["WATSON_UNDERSTANDING_USERNAME"],
        password=os.environ["WATSON_UNDERSTANDING_PASSWORD"],
    )

    return nlp_client.analyze(
        text=transcription["results"][0]["alternatives"][0]["transcript"],
        features=Features(
            categories=CategoriesOptions(),
            concepts=ConceptsOptions(),
            emotion=EmotionOptions(),
            entities=EntitiesOptions(),
            keywords=KeywordsOptions(),
            sentiment=SentimentOptions(),
        ),
    )
