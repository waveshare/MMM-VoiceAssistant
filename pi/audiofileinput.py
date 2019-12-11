# Copyright (C) 2018 Google Inc.
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

"""Simple file-based sample for the Google Assistant Service."""

import json
import logging
import os
import os.path
import sys
import pyaudio
import socket
import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
import googlesamples.assistant.grpc.audio_helpers as audio_helpers

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)

host = 'localhost'        # set ip
port = 2001                 # Set port

END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DEVICE_ID="xiaowei-7c15c"
DEVICE_MODEL_ID="xiaowei-7c15c-assistant-sdk-light-5n285y"

api_endpoint='embeddedassistant.googleapis.com'

device_model_id=DEVICE_MODEL_ID
device_id=DEVICE_ID
lang='en-US'
verbose=False
audio_sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
audio_sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
audio_iter_size=audio_helpers.DEFAULT_AUDIO_ITER_SIZE
audio_block_size=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
audio_flush_size=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
block_size=1024
grpc_deadline=300

@click.command()
@click.option('--input-audio-file', '-i', required=True,
              metavar='<input file>', type=click.File('rb'),
              help='Path to input audio file (format: LINEAR16 16000 Hz).')
@click.option('--output-audio-file', '-o', required=True,
              metavar='<output file>', type=click.File('wb'),
              help='Path to output audio file (format: LINEAR16 16000 Hz).')

def main(input_audio_file,output_audio_file):
    """File based sample for the Google Assistant API.

    Examples:
      $ python -m audiofileinput -i <input file> -o <output file>
    """
    # Setup logging.
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    credentials=os.path.join(click.get_app_dir('google-oauthlib-tool'),'credentials.json')
    
    # Load OAuth 2.0 credentials.
    try:
        with open(credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        sys.exit(-1)

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, api_endpoint)
    logging.info('Connecting to %s', api_endpoint)

    # Create gRPC stubs
    assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(grpc_channel)
    
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(2),
        channels=1,
        rate=16000, input=False, output=True)
    stream_out.start_stream()    
    # Generate gRPC requests.
    def gen_assist_requests(input_stream):
        dialog_state_in = embedded_assistant_pb2.DialogStateIn(
            language_code=lang,
            conversation_state=b''
        )
        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=16000,
                volume_percentage=100,
            ),
            dialog_state_in=dialog_state_in,
            device_config=embedded_assistant_pb2.DeviceConfig(
                device_id=device_id,
                device_model_id=device_model_id,
            )
        )
        # Send first AssistRequest message with configuration.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        while True:
            # Read user request from file.
            data = input_stream.read(block_size)
            if not data:
                break
            # Send following AssitRequest message with audio chunks.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)

    for resp in assistant.Assist(gen_assist_requests(input_audio_file),
                                 grpc_deadline):
        # Iterate on AssistResponse messages.
        if resp.event_type == END_OF_UTTERANCE:
            logging.info('End of audio request detected')
        if resp.speech_results:
            ts = ' '.join(r.transcript for r in resp.speech_results)
            logging.info('Transcript of user request: "%s".',ts)  
                            
        if resp.dialog_state_out.supplemental_display_text:
            logging.info('Assistant display text: "%s"',
                         resp.dialog_state_out.supplemental_display_text)
            s = socket.socket()         # creat socket
            s.connect((host, port))     # connect serve
            s.send(('I :'+ ts +'<br/>Robot :'+resp.dialog_state_out.supplemental_display_text).encode('UTF-8'))          # recieve data
            s.close()                  # Close the connection
        if len(resp.audio_out.audio_data) > 0:
            #Write assistant response to supplied file.
            #output_audio_file.write(resp.audio_out.audio_data)
            stream_out.write(resp.audio_out.audio_data)
        if resp.device_action.device_request_json:
            device_request = json.loads(resp.device_action.device_request_json)
            logging.info('Device request: %s', device_request)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

if __name__ == '__main__':
    main()
