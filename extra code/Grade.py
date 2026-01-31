# Author: Jack lidster
# Date: 2025-10-31
# Discription: Calculates the midterm grade of the student using this program
import math

choice = "0"

MAX_GRADE = 100
MIN_GRADE = 0

PREPARTORY_COUNT = 4
PREPARTORY_VALUE = 2

CLASS_EXCERCISE_COUNT = 4
CLASS_EXCERCISE_VALUE = 3

TEST_COUNT = 2
TEST_VALUE = 8

prepartory_list = list()
class_excercise_list = []
test_list = []

# input
for pa_count in range(PREPARTORY_COUNT):
    is_valid = False

    while not is_valid:
        try:
            user_input = float(input("enter your grade for Prepartory Activity " + str(pa_count + 1) + " (0-100): "))
            if MIN_GRADE <= user_input <= MAX_GRADE:
                prepartory_list.append(user_input)
                is_valid = True
            else:
                print("Error: Please enter your grade between " + str(MIN_GRADE) + " and " + str(MAX_GRADE) + ".")
        except:
            print("Error: Please enter your grade as a number.")
# output
pa_average = sum(prepartory_list) / PREPARTORY_COUNT
pa_score = (pa_average) / 100 * PREPARTORY_VALUE

# Input
for ce_count in range(CLASS_EXCERCISE_COUNT):
    is_valid = False

    while not is_valid:
        try:
            user_input = float(input("enter your grade for Class Excercise " + str(ce_count + 1) + " (0-100): "))
            if MIN_GRADE <= user_input <= MAX_GRADE:
                class_excercise_list.append(user_input)
                is_valid = True
            else:
                print("Error: Please enter your grade between " + str(MIN_GRADE) + " and " + str(MAX_GRADE) + ".")
        except:
            print("Error: Please enter your grade as a number.")
# Output
ce_average = sum(class_excercise_list) / CLASS_EXCERCISE_COUNT
ce_score = (ce_average) / 100 * CLASS_EXCERCISE_VALUE

# Input
for test_count in range(TEST_COUNT):
    is_valid = False

    while not is_valid:
        try:
            user_input = float(input("enter your grade for the Test " + str(test_count + 1) + " (0-100): "))
            if MIN_GRADE <= user_input <= MAX_GRADE:
                test_list.append(user_input)
                is_valid = True
            else:
                print("Error: Please enter your grade between " + str(MIN_GRADE) + " and " + str(MAX_GRADE) + ".")
        except:
            print("Error: Please enter your grade as a number.")
# Output
test_average = sum(test_list) / TEST_COUNT
test_score = (test_average) / 100 * TEST_VALUE


score = pa_score + ce_score + test_score
max_score = (PREPARTORY_COUNT*PREPARTORY_VALUE + CLASS_EXCERCISE_COUNT*CLASS_EXCERCISE_VALUE + TEST_COUNT*TEST_VALUE)
final_score = (score / max_score * 100)
grade = (final_score / max_score) * 100

print ("your avarage Prepatory Activity grade is " +str(round(pa_average,2)) + ".")
print ("your avarage Class Excercise grade is " +str(round(ce_average,2)) + ".")
print ("your avarage Test grade is " +str(round(test_average,2)) + ".")
print ("your your total score of weighted points is " +str(round(final_score,2)) + ".")
print ("your curent grade at your curent score is " +str(round(grade,2)) + ".")