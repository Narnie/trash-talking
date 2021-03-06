#!/usr/bin/env python

"""Dialogflow API Beta Detect Intent Python sample with an audio response.

Examples:
  python detect_intent_with_texttospeech_response_test.py -h
  python detect_intent_with_texttospeech_response_test.py \
  --project-id PROJECT_ID --session-id SESSION_ID "hello"
"""

import argparse
import uuid
import io
import os
import string
import sys
import pyaudio
import wave
import asyncio
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat
import subprocess
import whatisthat


# [START dialogflow_detect_intent_with_texttospeech_response]
async def detect_intent_with_texttospeech_response(project_id, session_id, texts,
                                             language_code):
    """Returns the result of detect intent with texts as inputs and includes
    the response in an audio format.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    import dialogflow_v2beta1 as dialogflow
    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path(project_id, session_id)
    print('Session path: {}\n'.format(session_path))

    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        # Set the query parameters with sentiment analysis
        output_audio_config = dialogflow.types.OutputAudioConfig(
            audio_encoding=dialogflow.enums.OutputAudioEncoding
            .OUTPUT_AUDIO_ENCODING_LINEAR_16)

        response = session_client.detect_intent(
            session=session_path, query_input=query_input,
            output_audio_config=output_audio_config)
        print('=' * 20)
        print('Query text: {}'.format(response.query_result.query_text))
        print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
        # The response's audio_content is binary.
        with open('output.wav', 'wb') as out:
            out.write(response.output_audio)
            print('Audio content written to file "output.wav"')
        print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
# [END dialogflow_detect_intent_with_texttospeech_response]


async def main():
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('what is that')
    recognizer.expect_phrase('what logo is that')
    recognizer.expect_phrase('what does that say')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()

    while True:
        print('Press the button and speak')
        button.wait_for_press()
        print('Listening...')
        text = recognizer.recognize()
        if text is None:
            print('Sorry, I did not hear you.')
        else:
            # Clear the output variable, so we don't repeat any previous results
            output = None
 
            # Determine what action to take
            if 'what is that' in text:
                output = whatisthat.takeAndProcessImage('label')
            elif 'what logo is that' in text:
                output = whatisthat.takeAndProcessImage('logo')
            elif 'what does that say' in text:
                output = whatisthat.takeAndProcessImage('text')
            elif 'goodbye' in text:
                break
            else:
                detect_intent_with_texttospeech_response('evil-bin', str(uuid.uuid4()), text, 'en-US')

            # If we got a result then both print and speak it. 
            if output is not None:
               print(output)
               aiy.audio.say(output)


# play text file
async def play(filename):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
    data = wf.readframes(chunk)
    while data != b'':
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()



async def maintest():
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
    parser.add_argument(
        'texts',
        nargs='+',
        type=str,
        help='Text inputs.')

    args = parser.parse_args()

    await detect_intent_with_texttospeech_response(
        args.project_id, args.session_id, args.texts, args.language_code)
    await play('output.wav')
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
