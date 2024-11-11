import os
import json
from dotenv import load_dotenv
from google.cloud import speech
from google.oauth2 import service_account

load_dotenv()


def get_google_cloud_credentials():
    service_account_json = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise EnvironmentError("Service account JSON not found in environment variables")

    credentials_dict = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
    return credentials


def transcribe_file(audio_file: str, credentials) -> speech.RecognizeResponse:
    try:
        client = speech.SpeechClient(credentials=credentials)
        print(f"Reading audio file: {audio_file}")
        with open(audio_file, "rb") as f:
            audio_content = f.read()
        
        # set the configuration of the audio file
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        print("Sending recognition request...")
        response = client.recognize(config=config, audio=audio)

        # print the result
        if response.results:
            for result in response.results:
                print(f"Transcript: {result.alternatives[0].transcript}")
        else:
            print("No transcription results found.")

        return response

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    credentials = get_google_cloud_credentials()
    transcribe_file("recording.wav", credentials)
