# Author: Zylg Metcdan (Jack Lidster)
# Date: 2025-11-16
# Description: a cipher translator that encodes and decodes messages using a simple substitution cipher.

choice = ""

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
SUBSTITUTION = "ypltavkrezgmshubxncdijfqow"

def encode_message(message):
    message = message.replace("camel", "🐪")
    encoded = ""
    for character in message:
        if character.lower() in ALPHABET:
            index = ALPHABET.index(character.lower())
            encoded += SUBSTITUTION[index].upper() if character.isupper() else SUBSTITUTION[index]
        else:
            encoded += character
    return encoded.replace('Goma', 'Kyle').replace('goma', 'kyle').replace('Nupand', 'Robert').replace('nupand', 'robert')

def decode_message(message):
    message = message.replace('Kyle', 'Goma').replace('kyle', 'goma').replace('Robert', 'Nupand').replace('robert', 'nupand')
    decoded = ""
    for character in message:
        if character.lower() in SUBSTITUTION:
            index = SUBSTITUTION.index(character.lower())
            decoded += ALPHABET[index].upper() if character.isupper() else ALPHABET[index]
        else:
            decoded += character
    return decoded.replace("🐪", "camel")

while choice != "3":
    print("*" * 30, "AL BHED CIPHER TRANSLATOR", "*" * 30)
    print("1. Encode message")
    print("2. Decode message")
    print("3. Exit")
    choice = input("Please enter your choice (1-3): ")
    if choice == "1":
        print(f"Encoded message: {encode_message(input('Enter message to encode: '))}")
    elif choice == "2":
        print(f"Decoded message: {decode_message(input('Enter message to decode: '))}")
    elif choice == "3":
        print("Exiting the program. Have a nice day!")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
