import random
import string


def passGen():
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
