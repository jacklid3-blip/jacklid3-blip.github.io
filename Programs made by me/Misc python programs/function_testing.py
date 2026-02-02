# Author:   Kyle Chapman
# Created:  March 13, 2024
# Updated by:  Robert Jack Baker Lidster
# Updated:  November 07, 2025
# Description:
# This is the base/tester file for a set of functions intended to
# be developed by students for the purpose of the Class Exercise
# for the functions unit in COSC 1100.
# While this file doesn't contain much in the way of functions,
# it is meant to reference functions included in a file named
# function_exercise.py in the same folder.
# If the student has succeeded at the exercise, this file should
# be completely unmodified.

# Imports.
import function_exercise as tests

# Declarations.
MINIMUM_VALUE = 0
MAXIMUM_VALUE = 100


# Function definition.
def test_list_functions(list_to_test: list):
    """This function exists strictly to test the is_list_numeric(), cap_list(), and drop_highest_and_lowest() functions. It produces a middle-weighted average of the list."""
    if tests.is_list_numeric(list_to_test):
        list_to_test = tests.cap_list(list_to_test, MINIMUM_VALUE, MAXIMUM_VALUE)
        list_to_test = tests.drop_highest_and_lowest(list_to_test)
        return list_to_test
    else:
        return []


# Establish the lists to test.
first_list = [100, 100, 0]
second_list = [100, 100, 100, 66.7, 100, 100, 0, 100, 0, 0, 0, 50]
third_list = [4, 100.5, -2, 99, 80, 100, 102]

# Run the function tests on each list.
first_list = test_list_functions(first_list)
second_list = test_list_functions(second_list)
third_list = test_list_functions(third_list)

# Print the output from the tests.
print("Test 1: " + str(first_list))
print("Test 2: " + str(second_list))
print("Test 3: " + str(third_list))

# to screw with kyle
if __name__ == "__main__":
    print("somthing")

# Confirm close.
input("\nPress Enter to end the program...")
