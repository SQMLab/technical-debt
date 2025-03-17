import hashlib

def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()
def common_white_space_prefix_index(lines):
    min_length = min(len(line) for line in lines)

    common_prefix_length = 0
    while common_prefix_length < min_length and all(line[common_prefix_length].isspace() for line in lines):
        common_prefix_length += 1
    return common_prefix_length

def to_text_without_leading_common_whitespace(lines):
    common_prefix_length = common_white_space_prefix_index(lines)
    return '\n'.join(line[common_prefix_length:] for line in lines)