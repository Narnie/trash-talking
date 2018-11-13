#!/usr/bin/env python
 
import listen
import textToSpeech
import argparse
import uuid
import io
import os
import string
import sys
import pyaudio
import wave
import asyncio

RATE = 24000

async def detect_intent_audio(project_id, session_id, audio_file_path,
                        language_code):
    """Returns the result of detect intent with an audio file as input.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    import dialogflow_v2beta1 as dialogflow

    session_client = dialogflow.SessionsClient()

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = RATE

    session = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session))

    with open(audio_file_path, 'rb') as audio_file:
        input_audio = audio_file.read()

    # Set the query parameters with sentiment analysis
    output_audio_config = dialogflow.types.OutputAudioConfig(
        audio_encoding=dialogflow.enums.OutputAudioEncoding
        .OUTPUT_AUDIO_ENCODING_LINEAR_16)

    audio_config = dialogflow.types.InputAudioConfig(
        audio_encoding=audio_encoding, language_code=language_code,
        sample_rate_hertz=sample_rate_hertz)
    query_input = dialogflow.types.QueryInput(audio_config=audio_config)

    response = session_client.detect_intent(
        session=session, query_input=query_input, output_audio_config=output_audio_config, 
        input_audio=input_audio)


    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))

    # The response's audio_content is binary.
    with open('output.wav', 'wb') as out:
        out.write(response.output_audio)
        print('Audio content written to file "output.wav"')

    # print('=' * 20)
    # print('Query text: {}'.format(response.query_result.query_text))
    # print('Detected intent: {} (confidence: {})\n'.format(
    #     response.query_result.intent.display_name,
    #     response.query_result.intent_detection_confidence))
    # print('Fulfillment text: {}\n'.format(
    #     response.query_result.fulfillment_text))
    # return [response.query_result.fulfillment_text]

async def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--project-id',
        help='Project/agent id.  Required.',
        required=True)
    parser.add_argument(
        '--session-id',
        help='Identifier of the DetectIntent session. '
             'Defaults to a random UUID.',
        default=str(uuid.uuid4()))
    parser.add_argument(
        '--language-code',
        help='Language code of the query. Defaults to "en-US".',
        default='en-US')

    args = parser.parse_args()

    sampleRate = listen.audio_int()
    filename = await listen.listen_for_speech()  # listen to mic.
    await detect_intent_audio(args.project_id, args.session_id, filename, args.language_code)
    # await textToSpeech.detect_intent_with_texttospeech_response(args.project_id, args.session_id, text, args.language_code)

        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    textToSpeech.play('output.wav')