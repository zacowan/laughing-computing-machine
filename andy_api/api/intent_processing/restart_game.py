"""
TODO add info about intent
"""

from .utils import get_random_choice
from api.state_manager import restart_game, set_fulfillment_params

HAPPY_PATH_RESPONSES = [
    "Are you sure you'd like to restart the game?",
    "Would you really like to start another round?"
]

def handle(session_id, board_str):
    static_choice = get_random_choice(HAPPY_PATH_RESPONSES)

    restart_game(session_id)

     # Log the fulfillment params
    set_fulfillment_params(session_id, params={
        "curr_board_str": board_str
    })

    return static_choice, True, board_str