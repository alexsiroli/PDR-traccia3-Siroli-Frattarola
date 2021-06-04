import enum


class Packet(enum.Enum):
    start = 2
    new_player = 1
    new_question_request = 3
    new_question = 4
    answer = 5
    player_score = 6
    player_left = 8
    game_over = 7
    new_player_name = 0
