# function to cap values in a list at a maximum of 100 with two prameters

list_to_cap = [0, 468, 9, -23, 101, 740, 100]
def cap_values(input_list, max_value=100):
    capped_list = []
    for value in input_list:
        if value > max_value:
            capped_list.append(max_value)
        else:
            capped_list.append(value)
    return capped_list
if __name__ == "__main__":
    result = cap_values(list_to_cap, 100)
    print(result)  # Output: [0, 100, 9, -23, 100, 100, 100]