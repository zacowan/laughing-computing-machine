"""This module handles the processing of audio files.

Attributes:
    BUCKET_NAME: the name of the bucket to upload user's audio to for STT.
    FILENAME_PREFIX: the directory in the bucket to store audio files for STT.
    FILE_TYPE: the type of the file to be processed for STT.
    FILE_SAMPLE_RATE: the sample rate of the file to be processed for STT.
    OUTPUT_FILE_NAME: the name of the file to output for TTS.

"""
import uuid

from google.cloud import speech, storage, texttospeech

BUCKET_NAME = "chess-to-speech"
FILENAME_PREFIX = "audio-files/"
FILE_TYPE = "audio/webm"
FILE_SAMPLE_RATE = 48000
OUTPUT_FILE_NAME = "andy_response.mp3"


def upload_audio_file(file_to_upload):
    """Uploads an audio file to gcloud storage.

    Args:
        file_to_upload (blob): the blob to upload.

    Returns:
        str: the name of the file uploaded.

    """
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob_name = FILENAME_PREFIX + str(uuid.uuid4())
        blob = bucket.blob(blob_name)

        blob.upload_from_string(file_to_upload, content_type=FILE_TYPE)

        return blob_name
    except Exception as err:
        print(err)
        raise


def generate_audio_response(text):
    """Converts text into an audio file.

    Args:
        text (str): the text to transform into audio.

    Returns:
        str: the location of the audio file generated.

    """
    try:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        with open(OUTPUT_FILE_NAME, "wb") as out:
            # Clear the contents of the file
            out.truncate(0)
            # Write the response to the output file.
            out.write(response.audio_content)

        return OUTPUT_FILE_NAME
    except Exception as err:
        print(err)
        raise


def transcribe_audio_file(file_to_transcribe):
    """Converts an audio file into text.

    Args:
        file_to_transcribe (blob): the blob to transcribe.

    Returns:
        str: the text interpreted from the audio.

    """
    try:
        client = speech.SpeechClient()

        file_name = upload_audio_file(file_to_transcribe)

        gcs_uri = "gs://" + BUCKET_NAME + "/" + file_name

        audio = speech.RecognitionAudio(uri=gcs_uri)

        # Note: the encoding and sample_rate_hertz should change based on what
        # file is expected.
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
            sample_rate_hertz=FILE_SAMPLE_RATE,
            language_code="en-US"
        )

        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

        return response.results[0].alternatives[0].transcript
    except Exception as err:
        print(err)
        raise
