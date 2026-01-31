# Author: Robert Jack Baker Lidster 
# Date: 2024-06-12
# Description: This module contains functions that perform various mathematical operations.


MIN_VALUE = 0
MAX_VALUE = 100

def is_list_numeric(input_list):
    """Check if all elements in the list are numeric (int or float)."""
    for item in input_list:
        if not isinstance(item, (int, float)):
            return False
    return True

def cap_list(list_to_cap, min_value, max_value):
    """Cap the values in the list to be within the specified min and max range."""
    return_list = []
    for value in list_to_cap:
        if value < min_value:
            return_list.append(min_value)
        elif value > max_value:
            return_list.append(max_value)
        else:
            return_list.append(value)
    return return_list

def drop_highest_and_lowest(input_list):
    """Remove the highest and lowest values from the list."""
    if len(input_list) <= 2:
        return []
    sorted_list = sorted(input_list)
    return sorted_list[1:-1]

# Dear Kyle if you are reading this, I request that you put your favorite type of camel in the area where you grade this assignment. Thank you! and have a nice day!
# Also 🐪
if __name__ == "__main__":
    print("Your runing the wrong file YOU CAMEL!")
input("Press Enter to accept that you are a Camel...")
print("Goodbye Camel!")