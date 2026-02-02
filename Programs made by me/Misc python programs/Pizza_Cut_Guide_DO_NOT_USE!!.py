# Author: Jack Lidster
# Date: 2025/10/17
# Description: A user enters the diamiter of a pizza in the range of 8 to 24
# the Program then responds with the number of slices for that size of pizza the range being
# that of 6, 8, 10, 12, and 16. the program at the same time tells the user the area of each slice depending on how many slices are cut and how big the pizza is

import math

user_input = "1"
diamiter = "0"

MAX_DIAMITER = 24
MIN_DIAMITER = 8

SMALL_SLICE = 6
MEDIUM_SLICE = 8
LARGE_SLICE = 10
EXTRA_LARGE_SLICE = 12
MAX_SLICE = 16

while not user_input == "0":
    print(f'Maximum diamiter is {MAX_DIAMITER}\"')
    print(f'Minimum diamiter is {MIN_DIAMITER}\"')
    user_input = input('Please enter the diameter of your pizza (0 to end program)')
    if user_input == "0":
        continue
    try:
        diamiter = float(user_input)
        if MIN_DIAMITER <= diamiter <= MAX_DIAMITER:
            # Calculate pizza area
            area = math.pi * (diamiter/2)**2
            def get_slices(size):
                if 8.0 <= size < 10.0:
                    return [SMALL_SLICE]
                if 10.0 <= size < 14.0:
                    return [SMALL_SLICE, MEDIUM_SLICE]
                if 14.0 <= size < 16.0:
                    return [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE]
                if 16.0 <= size < 20.0:
                    return [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE]
                else:
                    return [SMALL_SLICE, MEDIUM_SLICE, LARGE_SLICE, EXTRA_LARGE_SLICE, MAX_SLICE]
            slices = get_slices(diamiter)
            print(f'Pizza diameter: {diamiter}" — Total area: {area:.2f} sq in')
            for s in slices:
                slice_area = area / s
                print(f'{s} slices -> {slice_area:.2f} sq in per slice')
        else:
            print(f'(Entry Error) please enter a diameter in the range of {MIN_DIAMITER}" to {MAX_DIAMITER}" please try again')
    except:
        print("Invalid input. Please enter a valid number.")
        continue