#!/usr/bin/env python3

import os
from google.cloud import texttospeech

def generate_speech():
    print('Generate mp3 audio assets from text')

    client = texttospeech.TextToSpeechClient()

    languages = {
        "English": {
            "code": "en-GB",
            "voice": 'en-GB-Neural2-A'
        },
        "French":{
            "code": "fr-FR",
            "voice": "fr-FR-Neural2-A"
        },
        "Arabic": {
            "code": "ar-AR",
            "voice": "ar-XA-Wavenet-D"
        }
    }

    language = input("Choose a language (English, French, Arabic): ")
    if language not in languages:
        print("Invalid language")
        exit()

    text = input("Text to synthesize: ")
    out_dir = input("Output directory: ")
    file_name = input("File name of the generated asset: ")

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=languages[language]["code"],
        name=languages[language]["voice"],
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    if response:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        dest = os.path.join(out_dir, file_name if ".mp3" in file_name else file_name + ".mp3")

        with open(dest, "wb") as f:
            f.write(response.audio_content)
        print("Audio file generated successfully")
    else:
        print("Failed to generate audio file", response)


if __name__ == "__main__":
    generate_speech()