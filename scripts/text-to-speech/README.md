# Text-To-Speech asset generation

This script can be used to generate audio assets using Google Cloud Text-To-Speech.<br>
To  use it you need to have activated the Text-To-Speech API and created a service account for a Google Cloud project, all of which is explained [here](https://cloud.google.com/text-to-speech/docs/before-you-begin).

## Setup

### Google Cloud authentication
1. [Download a JSON key for your service account](https://cloud.google.com/text-to-speech/docs/before-you-begin#create_a_json_key_for_your_service_account)
2. Create an `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to your JSON key:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="<path to the downloaded service account key>"
```

### Dependencies
Run `pip install -r requirements.txt` to install the script's dependencies.

## Running the script
Run `./text_to_speech.py` or `python3 text_to_speech.py` and follow the instructions to generate assets to the desired location.