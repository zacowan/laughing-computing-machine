import chess
import chess.engine
import os

# This is a relative location to the directory in which you run the script (aka, andy_api/)
STOCKFISH_ENGINE_LOCATION = os.environ.get("STOCKFISH_LOCATION")

if not STOCKFISH_ENGINE_LOCATION:
    raise Exception("You need to specify a location for the stockfish engine.")

CHESS_PIECE_NAMES = {
    'P': 'pawn',
    'R': 'rook',
    'N': 'knight',
    'B': 'bishop',
    'Q': 'queen',
    'K': 'king'
}


def get_engine():
    return chess.engine.SimpleEngine.popen_uci(STOCKFISH_ENGINE_LOCATION)


def get_best_move(board_str):
    engine = get_engine()
    board = chess.Board(board_str)
    best_move = engine.play(board, chess.engine.Limit(time=0.1)).move
    engine.quit()
    return best_move.uci()


def get_board_str_with_move(board_str, move_sequence):
    board = chess.Board(board_str)
    board.push_uci(move_sequence.lower())
    return board.fen()


def get_piece_name_at(board_str, location):
    board = chess.Board(board_str)
    board_location = chess.parse_square(location)
    piece_symbol = board.piece_at(board_location).symbol()
    return CHESS_PIECE_NAMES.get(piece_symbol.upper(), 'unknown piece')


def check_if_check(board_str):
    board = chess.Board(board_str)
    return board.is_check()


def check_if_checkmate(board_str):
    board = chess.Board(board_str)
    return board.is_checkmate()


def get_current_color_turn(board_str):
    board = chess.Board(board_str)
    return board.turn


def get_piece_at(board_str, location):
    board = chess.Board(board_str)
    board_location = chess.parse_square(location.lower())
    return board.piece_at(board_location)


def check_if_turn(board_str, location):
    board = chess.Board(board_str)
    board_location = chess.parse_square(location.lower())
    return board.turn == board.color_at(board_location)


def check_if_move_legal(board_str, move_sequence):
    board = chess.Board(board_str)
    try:
        return chess.Move.from_uci(move_sequence.lower()) in board.legal_moves
    except ValueError:
        return False


def check_if_move_causes_check(board_str, move_sequence):
    board = chess.Board(board_str)
    move_to_make = chess.Move.from_uci(move_sequence.lower())
    if move_to_make in board.pseudo_legal_moves:
        return True
    else:
        return False


def get_from_location_from_piece_name_and_to_location(board_str, move_info):
    board = chess.Board(board_str)

    to_location = move_info.get("to_location").lower()
    piece_name = move_info.get("piece_name")

    # Get a list of all possible from locations based on to_location
    potential_from_locations = []
    for move in board.pseudo_legal_moves:
        to_square_name = chess.square_name(move.to_square())
        from_square_name = chess.square_name(move.from_square())
        if to_square_name.lower() == to_location:
            potential_from_locations.append(from_square_name)

    # Only a single possible move
    if len(potential_from_locations) == 1:
        return potential_from_locations[0]
    elif not piece_name:
        # Don't know what piece to move
        return None

    # Need to cross-reference with piece name
    new_potential_from_locations = []
    for from_loc in potential_from_locations:
        piece = board.piece_at(chess.parse_square(from_loc))
        pname = CHESS_PIECE_NAMES.get(piece.symbol().lower())
        if pname == piece_name.lower():
            new_potential_from_locations.append(from_loc)

    if len(new_potential_from_locations) == 1:
        return new_potential_from_locations[0]
    else:
        # Don't know what piece to move
        return None
