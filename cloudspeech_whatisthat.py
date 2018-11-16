#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google CloudSpeech recognizer."""

import aiy.audio
import aiy.cloudspeech
import aiy.voicehat
import subprocess
import asyncio
from rekognise import takeAndProcessImage
import subprocess

def say(text):
    subprocess.call(['/home/pi/voice-synth/synth', text])
    

def queryDialogueFlow(text):

    import dialogflow_v2beta1 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path('evil-bin', '123')
    
    text_input = dialogflow.types.TextInput(
            text=text, language_code='en-US')

    query_input = dialogflow.types.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
            session=session, query_input=query_input)

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
    return response.query_result.fulfillment_text
def main():
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('what is that')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()

    while True:
        print('Press the button and speak')
       # button.wait_for_press()
       # response = queryDialogueFlow("Ok Bender Bin")
       # say(response)
       # button.wait_for_press()
       # tags = takeAndProcessImage()
       # print(tags)
       # response = queryDialogueFlow(tags[0])

        #say(response)
        button.wait_for_press()
        print('Listening...')
        text = recognizer.recognize()
        print('You said "', text, '"')
        if 'hello' in text:
            response = queryDialogueFlow("Ok Bender Bin")
            say(response)
        else: 
            response = queryDialogueFlow(text)
            say(response)


if __name__ == '__main__':
    main()
