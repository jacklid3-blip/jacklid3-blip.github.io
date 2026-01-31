# Author: Jack Lidster
# Date: 9/12/2025
# Description: This program calculates the total hours and revenue for a dog grooming business based on user input.

# Unless TIME ITSELF changes. DO NOT TOUCH!
TIME_PER_HOUR = 60

basic_washes = int(input ("Input the number of basic wash and brush services, for the week:"))

# Edit this to change the time
BASIC_TIME = 30
# Edit this to change the cost
BASIC_COST = 35

total_time_for_basic = (basic_washes * BASIC_TIME)
total_hours_for_basic = (total_time_for_basic / TIME_PER_HOUR)
total_cost_for_basic = (basic_washes * BASIC_COST)

full_washes = int(input ("Input the number of full groom services, for week:"))

# Edit this to change the time
FULL_TIME = 60
# Edit this to change the cost
FULL_COST = 50

total_time_for_full = (full_washes * FULL_TIME)
total_hours_for_full = (total_time_for_full / TIME_PER_HOUR)
total_cost_for_full = (full_washes * FULL_COST)

deluxe_washes = int(input ("Input the number of deluxe spa services, for the week:"))

# Edit this to change the time
DELUXE_TIME = 90
# Edit this to change the cost
DELUXE_COST = 70

total_time_for_deluxe = (deluxe_washes * DELUXE_TIME)
total_hours_for_Deluxe = (total_time_for_deluxe / TIME_PER_HOUR)
total_cost_for_deluxe = (deluxe_washes * DELUXE_COST)

print("the total hours for basic wash and brush services is", total_hours_for_basic, "hours. and the total cost is $", total_cost_for_basic) 
print("the total hours for full groom services is", total_hours_for_full, "hours. and the total cost is $", total_cost_for_full)
print("the total hours for deluxe spa services is", total_hours_for_Deluxe, "hours. and the total cost is $", total_cost_for_deluxe)

total_hours = (total_hours_for_basic + total_hours_for_full + total_hours_for_Deluxe)

total_cost = (total_cost_for_basic + total_cost_for_full + total_cost_for_deluxe)

print("the total hours for all services this week is", total_hours, "hours. and the total revenue is $",round(total_cost,2))

input ("Press Enter to exit")