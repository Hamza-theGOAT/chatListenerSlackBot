import random
import string


def passGen():
    """
    Generate a strong random password.

    The function creates a 13-character random password containing
    a mix of uppercase letters, lowercase letters, digits, and symbols.
    It guarantees inclusion of characters from all four sets to maximize entropy,
    then fills the rest of the password with random characters from the combined set.

    Process:
    - Defines four character sets: uppercase, lowercase, digits, and symbols.
    - Randomly samples all sets to ensure diversity.
    - Selects one random character from each chosen set.
    - Adds 12 additional random characters from the combined sets.
    - Shuffles the characters to remove ordering patterns.
    - Returns the password as a string.

    Returns:
        str: A randomized, secure password.

    Example:
        >>> passGen()
        "A2g@D$e1J{9q"

    Notes:
        - Current implementation produces a 13-character password (1 from each set + 12 extra).
        - To adjust length or complexity, modify the number of additional characters added.
        - The symbol set includes characters often disallowed in certain systems;
          consider pruning if targeting specific services.
    """
    # Define character sets
    upperCase = string.ascii_uppercase
    lowerCase = string.ascii_lowercase
    numbers = string.digits
    symbols = "!@#$%^&*.:;~'`\"*/\\+?-,_|=()[]{}<>"

    # Ensure at least 3 different types are included in the password
    chosenSets = random.sample([upperCase, lowerCase, numbers, symbols], 4)
    print(f"Choosen Sets: {chosenSets}")

    # Ensure the password is 12 characters long: one from each set thrice
    password = [random.choice(s) for s in chosenSets]

    # Add additional 9 characters from combined chosen sets
    combined = ''.join(chosenSets)
    password += random.choices(combined, k=12)

    # Shuffle to avoid predictable sequences
    random.shuffle(password)

    return ''.join(password)


if __name__ == '__main__':
    randKey = passGen()
    print(f'\nGenerated Password: {randKey}')
