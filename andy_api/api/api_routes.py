"""This module contains all of the routes accessible to the client.

Attributes:
    bp: The blueprint that the __init__.py will use to handle routing.

"""
from flask import (
    Blueprint, request, jsonify
)

from . import speech_text_processing, dialogflow_andy
from .intent_processing import intent_processing

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/get-audio-response", methods=["POST"])
def get_audio_response():
    if request.method == "POST":
        # TODO: use session_id for logging
        session_id = request.args.get('session_id')
        # Convert response to audio
        response_audio = speech_text_processing.generate_audio_response(
            request.data)
        return response_audio


@bp.route("/get-response", methods=["POST"])
def get_response():
    """Route for getting a response from Andy and any actions to take.

    Query Params:
        session_id: the unique session ID to use with Andy.
        board_str: FEN representation of board from client

    Body:
        A Blob that contains the audio to interpret.

    Returns:
        An HTTP response, with the data field containing a JSON object. The data
        field will only be present if the status code of the response is 200.

        {
            'response_text': str,
            'response_audio': str,
            'board_str': str
            'fulfillment_info': dict
        }

        response_text (str): the response generated by Andy, as text.
        fulfillment_info (dict): the intent information detected from the user
            and the game state.

            {
                'intent_name': str,
                'success': boolean
            }

            intent_name (str): the name of the detected intent.
            success (boolean): whether or not the fulfillment for the intent was
                performed successfully.
        board_str (str): the state of the board, as a FEN string.

    """
    if request.method == "POST":
        session_id = request.args.get('session_id')
        # grab board string from HTTP arguments
        board_str = request.args.get('board_str')

        # Get text from audio file
        transcribed_audio = speech_text_processing.transcribe_audio_file(
            request.data)

        # Detect intent from text
        intent_query_response = None
        if transcribed_audio is not None:
            intent_query_response = dialogflow_andy.perform_intent_query(
                session_id, transcribed_audio)

        # Determine Andy's response
        response_text, fulfillment_info, updated_board_str = intent_processing.fulfill_intent(
            intent_query_response, board_str)

        # TODO: Get updated board string

        return jsonify({
            'response_text': response_text,
            'board_str': board_str,  # include updated board string in JSON response
            'fulfillment_info': fulfillment_info,
            'board_str': updated_board_str,
        })
