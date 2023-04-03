import random
import string

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


def random_upper_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_uppercase, k=length))


def random_number(start: int = 100, end: int | None = None):
    if end:
        if start > end:
            return random.randrange(start=end, stop=start + 1)
        else:
            return random.randrange(start=start, stop=end + 1)
    else:
        return random.randrange(start=1, stop=start)
