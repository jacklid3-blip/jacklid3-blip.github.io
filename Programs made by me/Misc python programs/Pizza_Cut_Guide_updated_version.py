# Author: Jack Lidster
# Date: 2025/10/17
# Old Grade: 6/12
# Updated: 2025/11/12
# New Grade: 12/12
# Curent Mark afrer Update: 9/12
# Description: A user enters the diamiter of a pizza in the range of 8 to 24
# the Program then responds with the number of slices for that size of pizza the range being
# that of 6, 8, 10, 12, and 16. the program at the same time tells the user the area of each slice depending on how many slices are cut and how big the pizza is
import math

user_input = "1"
diameter = 0
slices = []

MAX_DIAMETER = 24
MIN_DIAMETER = 8

SMALL_SLICE = 6
SMALL_SIZE = 8
MEDIUM_SLICE = 8
MEDIUM_SIZE = 12
LARGE_SLICE = 10
LARGE_SIZE = 14
EXTRA_LARGE_SLICE = 12
EXTRA_LARGE_SIZE = 16
EXTRA_EXTRA_LARGE_SLICE = 14
EXTRA_EXTRA_LARGE_SIZE = 20
MAX_SLICE = 16
MAX_SIZE = 24

while not user_input == "0":
    print(f'Maximum diameter is {str(MAX_DIAMETER)}"')
    print(f'Minimum diameter is {str(MIN_DIAMETER)}"')
    user_input = input('Please enter the diameter of your pizza (0 to end program): ')
    if user_input == ("🐫"):
        print("Camel detected!")
        print("[WARNING] You can not have a camel in your computer! System Error [SHUTTING DOWN]")
        user_input = "0"
    elif user_input == ("🐪"):
        print("Camel detected!")
        print("[WARNING] You can not have a camel in your computer! System Error [SHUTTING DOWN]")
        user_input = "0"
    elif user_input == ("Kyle"):
        print("Hey Kyle! You expected an error but insted you got to press enter to see what you get instead")
        input("Press Enter to see what i have got in store for you...")
        print("its a CAMEL! 🐫")
        input("Press Enter To scan the camel...")
        print("Scaning...")
        print("Scan complete!")
        print("[WARNING] You have too much camel your System can not handle it! Error code: 78.9 [SHUTTING DOWN]")
        user_input = "0"
    if user_input != "0":
        try:
            diameter = float(user_input)
            if MIN_DIAMETER <= diameter <= MAX_DIAMETER:
                diameter_int = int(diameter)
                if SMALL_SIZE <= diameter_int < MEDIUM_SIZE:
                    slices = [SMALL_SLICE]
                elif MEDIUM_SIZE <= diameter_int < LARGE_SIZE:
                    slices = [SMALL_SLICE, MEDIUM_SLICE]
                elif LARGE_SIZE <= diameter_int < EXTRA_LARGE_SIZE:
                    slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE]
                elif EXTRA_LARGE_SIZE <= diameter_int < EXTRA_EXTRA_LARGE_SIZE:
                    slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE]
                elif EXTRA_EXTRA_LARGE_SIZE <= diameter_int <= MAX_SIZE:
                    slices = [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE, MAX_SLICE]
                for slice_count in slices:
                    area = math.pi * (diameter / 2) ** 2
                    slice_area = area / slice_count
                    print(f'{slice_count} slices -> {slice_area:.2f} ²in per slice')
                print(f'Pizza diameter: {diameter}" — Total area: {area:.2f} ²in ')
            else:
                print(f'(Entry Error) please enter a diameter in the range of {MIN_DIAMETER}" to {MAX_DIAMETER}" please try again')
        except:
            print("Invalid input. Please enter a valid number. and no camels and or other emojis are not vaild inputs.")