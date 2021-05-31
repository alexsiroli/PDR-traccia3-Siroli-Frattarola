VALUE_END = '$'
KEY_END = '='


def decode(string):
    string = str(string)
    actual_word = ""
    decoded = {}
    key = ""
    for c in string:
        if c == KEY_END:
            key = actual_word
            actual_word = ""
        elif c == VALUE_END:
            decoded[key] = actual_word
            key = ""
            actual_word = ""
        else:
            actual_word += c
    decoded[key] = actual_word
    return decoded


def encode(values):
    string = ""
    for v in values:
        string += str(v['key']) + KEY_END + str(v['value']) + VALUE_END
    return string[:-1]

# print(decode("ciao=1$bau=2"))
# dictionary = [{'key': "marco", 'value': 4}, {'key': "arr", 'value': 4}]
# print(encode(dictionary))
