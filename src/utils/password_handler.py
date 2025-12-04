# src/views/utils/password_handler.py

import random
import string


def create_strong_password(length: int = 30) -> str:
    """
    Generates a strong, random password that meets the following criteria:
    1. Contains at least one lowercase letter (a-z).
    2. Contains at least one uppercase letter (A-Z).
    3. Contains at least one digit (0-9).
    4. Contains at least one special character from the set @$!%*?&.

    Args:
        length (int): The desired length of the password (minimum is 4).

    Returns:
        str: The generated password.
    """
    LOWERCASE = string.ascii_lowercase
    UPPERCASE = string.ascii_uppercase
    DIGITS = string.digits
    SPECIAL_CHARS = "@$!%*?&"
    ALL_CHARS = LOWERCASE + UPPERCASE + DIGITS + SPECIAL_CHARS
    if length < 4:
        length = 4
    required_chars = [
        random.choice(LOWERCASE),
        random.choice(UPPERCASE),
        random.choice(DIGITS),
        random.choice(SPECIAL_CHARS),
    ]
    remaining_length = length - len(required_chars)
    random_chars = [random.choice(ALL_CHARS) for _ in range(remaining_length)]
    password_list = required_chars + random_chars
    random.shuffle(password_list)
    return "".join(password_list)
