VALUE_END = '$'
KEY_END = '='


# ritorna un dizionario da una stringa
def decode(string):
    string = string.decode()
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


# ritorna una stringa da un dizionario
def encode(values):
    string = ""
    i = 0
    print(values)
    for k in values.keys():
        string += (str(k) + KEY_END + str(values[k]) + VALUE_END)
    return string[:-1].encode()

