import socket
import packet_type as pt

VALUE_END = '$'
KEY_END = '='


# returns a dictionary with key-values from the string
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


# return a string from a dictionary
def encode(values):
    string = ""
    i = 0
    print(values)
    for k in values.keys():
        string += (str(k) + KEY_END + str(values[k]) + VALUE_END)
    return string[:-1].encode()

# print(decode("ciao=1$bau=2"))
# dictionary = {'marco': 4, 'p_id' : pt.Packet.start.value}
# print(encode(dictionary))
