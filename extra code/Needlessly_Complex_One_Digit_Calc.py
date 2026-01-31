# Author: Jack Lidster & Michael Tasson
# Date: 09-26-2025
# Description: needlessly complicated one-digit calculator.

# Information Logic - I didn't want to do print statments..

info = []
info.append(" ")
info.append("Hello and welcome to this needlessly complicated one digit calculator. :D")
info.append(" ")
info.append("1. This program will only accept one-digit calculations.")
info.append("2. These calculations will only use intergers from 0 to 9")
info.append("3. It only allows these mathematical operators such as: ")
info.append(" ")
info.append("[+] Addition, [-] Subtraction, [*] Multiplication & [/] Division.")
info.append(" ")
for item in info:
  print(item)

# Error Messages

not_vaild_three_digit_number = "Please enter a vaild three-digit equation (no empty strings, no letters, no decimals & no emojis)."
not_vaild_operator = "Please enter a vaild operator."

can_not_divide_by_zero = "You cannot divide zero by zero."


# Vaild Operators

valid_operators = ['+', '-', '*', '/',]

# User Input

user_input = input("Please enter your three digit equation here: ").strip()
if user_input == "🐫/2":
    print("🐫 / 2 = 🐪") 
    input("Press 'Enter' to leave this camel. (you won't) ")
    exit()
else:
    pass
# Check if the equation is the length of 3

if len(user_input) == 3:
    if user_input [0].isnumeric() and user_input [2].isnumeric():
        if user_input[1] in valid_operators:
            pass # Continue the program
        else:
            print(not_vaild_operator)
            input("Press 'Enter' to end this program. :D ")
            exit()
    else:
        print(not_vaild_three_digit_number)
        input("Press 'Enter' to end this program. :D ")
        exit()
else:
    print(not_vaild_three_digit_number)
    input("Press 'Enter' to end this program. :D ")
    exit()

# Check if first & third strings are numbers

first_digit = int(user_input[0])
operator = user_input[1]
second_digit = int(user_input[2])

# Math logic

if operator == "+":
    print(f"{first_digit} + {second_digit} = {first_digit + second_digit}")
if operator == "-":
    print(f"{first_digit} - {second_digit} = {first_digit - second_digit}")
if operator == "*":
    print(f"{first_digit} * {second_digit} = {first_digit * second_digit}")
if operator == "/":
  
    if second_digit == 0:
        print(can_not_divide_by_zero)
    else:
        print(f"{first_digit} / {second_digit} = {first_digit / second_digit}")


input("Press 'Enter' to end this program. :D ")