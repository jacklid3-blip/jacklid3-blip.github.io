# Author: Jack Lidster 
# Date: 2025-12-10
# Description: a function that takes a list and removes the two lowest values from it and returns the modified list

list_to_test = [78, 156, 0, 1566, 0, -1]

def remove_two_lowest(input_list):
    if len(input_list) <= 2:
        return []
    return_list = input_list.copy()
    for _ in range(2):
        lowest_value = min(return_list)
        return_list.remove(lowest_value)
    return return_list
result = remove_two_lowest(list_to_test)

print("Original list:", list_to_test)
print("Modified list:", result)

