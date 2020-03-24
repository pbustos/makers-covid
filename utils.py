import unidecode


def char_range(from_to, row=None):
    c1 = from_to[0]
    c2 = from_to[1]
    char_range = []
    for c in range(ord(c1), ord(c2)+1):
        if row is not None:
            char_range.append(chr(c)+str(row))
        else:
            char_range.append(chr(c))
    return char_range

def char_to_index(char):
    char = char.upper()
    index = ord(char)-ord('A')+1
    return index

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def clean_and_map_header(header, map):
    new_header = header.strip()
    if new_header in map:
        new_header = map[new_header]
    new_header = remove_special_chars(new_header)
    return new_header.lower()

def remove_special_chars(text):
    if isinstance(text, str):
        return unidecode.unidecode(text)
    else:
        return text

def reasign_type(types, intput_array):
    result = [0 if method == 'int' and (input == '' or input is None) else eval(method)(input) for method, input in zip(types, intput_array)]
    return result