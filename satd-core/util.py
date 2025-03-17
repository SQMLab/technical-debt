import hashlib


def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()


def common_white_space_prefix_index(lines):
    filtered_lines = [line for line in lines if line != '\n']

    if len(filtered_lines) == 0:
        return 0
    min_length = min(len(line) for line in filtered_lines)

    common_prefix_length = 0
    while common_prefix_length < min_length and all(line[common_prefix_length].isspace() for line in filtered_lines):
        common_prefix_length += 1
    return common_prefix_length


def to_text_without_leading_common_whitespace(lines):
    common_prefix_length = common_white_space_prefix_index(lines)
    code_block = ''.join(line[common_prefix_length:] if common_prefix_length < len(line) else line for line in lines)
    if len(code_block) > 0 and code_block[-1] == '\n':
        return code_block[:-1]
    else:
        return code_block

def get_first_n_line(text, n):
    lines = text.split('\n')
    return '\n'.join(lines[:min(len(lines),n)])

def get_last_n_line(text, n):
    lines = text.split('\n')
    return '\n'.join(lines[max(0,len(lines) - n):])