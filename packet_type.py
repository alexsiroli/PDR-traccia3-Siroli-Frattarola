import enum


class Packet(enum.Enum):
    start = 0
    new_player = 1
    new_question_request = 2
    new_question = 3
    answer = 4
    player_score = 5
    player_left = 6
    game_over = 7
    new_player_name = 8
