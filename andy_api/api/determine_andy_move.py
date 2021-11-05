"""This module will determine what Andy's move will be.

"""
from .intent_processing.utils import get_random_choice
import chess
import os


HAPPY_PATH_RESPONSES = [
    "I'll move my {piece_name} at {from_location} to {to_location}",
    "Let me move my {piece_name} from {from_location} to {to_location}"
]

def get_engine():
    dirname = os.path.dirname(__file__)
    engine_filename = dirname + "/UCI_engine/stockfish"
    engine = chess.engine.SimpleEngine.popen_uci(engine_filename) #load stockfish as chess engine
    return engine

def get_best_move(board_str):
    engine = get_engine()
    board = chess.Board(board_str)
    bestMove = engine.play(board, chess.engine.Limit(time=0.1)).move
    engine.close()
    return bestMove

def make_move(board_str, move):
    board = chess.Board(board_str)
    board.push(chess.Move.from_uci(move))
    return board.board_fen


def determine_andy_move(board_str):
    """Handles determining a text response for Andy's move.

    Args:
        board_str: the state of the board, as text.

    Returns:
        str: the response that should be given, as text.
        str: the updated board_str that should be given.

    """
    static_choice = get_random_choice(HAPPY_PATH_RESPONSES)

    move = get_best_move(board_str)

    from_location = move[0:2]
    to_location = move[2:4]

    updated_board_str = make_move(move)

    new_board = chess.Board(updated_board_str)
    piece_name = new_board.piece_at(to_location)

    if(new_board.is_check()):
        return "I'll move my {piece_name} at {from_location} to {to_location}... I got ya in check!", updated_board_str

    if(new_board.is_checkmate):
        return "Let me move my {piece_name} from {from_location} to {to_location}... And... I win!", updated_board_str

    # check if board is check

    return static_choice.format(
        from_location=from_location,
        to_location=to_location,
        piece_name=piece_name), updated_board_str
