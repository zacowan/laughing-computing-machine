"""This module processes intents and determines a text response.

Attributes:
    STATIC_RESPONSES (dict): a dictionary of lists for static response types.

Example Intent Model:
    {
        query_text: "I\'ll take white side."
        parameters {
            fields {
                key: "BoardSide"
                value {
                    string_value: "white"
                }
            }
        }
        all_required_params_present: true
        fulfillment_text: "Great, you\'ll play white side then!"
        fulfillment_messages {
            text {
                text: "Great, you\'ll play white side then!"
            }
        }
        intent {
            name: "projects/chess-master-andy-mhyo/agent/intents/6fafe557-d27b-41e7-bef0-204a87036e2c"
            display_name: "Choose Side Intent"
        }
        intent_detection_confidence: 1.0
        language_code: "en"
    }

"""
from api.state_manager import get_game_state
from .utils import INTENT_MAPPING, RESPONSE_TYPES, get_random_choice
from . import choose_side, move_piece_from, move_piece_to, wake_up_phrase


STATIC_RESPONSES = {
    RESPONSE_TYPES.HELLO: [
        "Hi! How are you?",
        "Hey, what's up?",
        "Yo, how's it going?"
    ],
    RESPONSE_TYPES.FALLBACK: [
        "I didn't get that. Can you say it again?",
        "I missed what you said. What was that?",
        "Sorry, could you say that again?",
        "Can you say that again?",
        "One more time?",
        "What was that?",
        "Say that one more time?",
        "I'm not sure I understood that."
    ]
}


def fulfill_intent(session_id, board_str, intent_data):
    """Fulfills an intent, performing any actions and generating a response.

    Args:
        session_id (str): the session ID provided by the client.
        board_str (str): the FEN string representation of the board.
        intent_data (dict): the intent query response generated by Dialogflow.

    Returns:
        str: the response that should be given, as text.
        dict: the internal name of the intent and the success of its
            fulfillment.

    """
    # Determine the response type from the intent
    try:
        response_type = INTENT_MAPPING.get(
            intent_data.intent.name, RESPONSE_TYPES.FALLBACK)
    except Exception:
        response_type = RESPONSE_TYPES.FALLBACK

    response_choice = get_random_choice(
        STATIC_RESPONSES.get(RESPONSE_TYPES.FALLBACK))
    success = False
    updated_board_str = board_str

    # Get the game state
    game_state = get_game_state(session_id)

    # Intents to handle at any stage of an interaction
    if response_type == RESPONSE_TYPES.FALLBACK:
        response_choice = get_random_choice(
            STATIC_RESPONSES.get(response_type))
        success = True

    # Intents to handle before the game has started
    if not game_state["game_started"]:
        if response_type == RESPONSE_TYPES.WAKE_UP_PROMPT:
            response_choice, success = wake_up_phrase.handle()
        elif response_type == RESPONSE_TYPES.WAKE_UP_FOLLOW_UP_YES:
            response_choice, success = wake_up_phrase.handle_yes()
        elif response_type == RESPONSE_TYPES.WAKE_UP_FOLLOW_UP_NO:
            response_choice, success = wake_up_phrase.handle_no()
        elif response_type == RESPONSE_TYPES.CHOOSE_SIDE:
            response_choice, success, updated_board_str = choose_side.handle(
                session_id, intent_data)

    # Intents to handle after a game has started and the user has chosen a side
    elif not game_state["game_finished"]:
        if response_type == RESPONSE_TYPES.MOVE_PIECE_FROM:
            response_choice, success, updated_board_str = move_piece_from.handle(
                session_id, intent_data, board_str)
        elif response_type == RESPONSE_TYPES.MOVE_PIECE_TO:
            response_choice, success, updated_board_str = move_piece_to.handle(
                session_id, intent_data, board_str)

    # Intents to handle after a game has finished
    else:
        # PLACEHOLDER
        response_choice = get_random_choice(
            STATIC_RESPONSES.get(response_type))
        success = True

    # Return the determined response
    return response_choice, {
        'intent_name': response_type.name,
        'success': success
    }, updated_board_str
