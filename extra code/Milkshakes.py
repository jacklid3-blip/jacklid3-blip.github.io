# date: 2025-10-03
# author: Jack Lidster, Anthony S
# description: 
# asks the user for ammount and type of milkshake
# then prints the ammount and percent of which flavour is ordered
# no break statements used

print("*"*30, "DROWN IN MILKSHAKES", "*"*30)

choice = "0"

chocolate = 0
vanilla = 0
strawberry = 0

while choice != "4":
    print("1. Chocolate") 
    print("2. Vanilla")
    print("3. Strawberry")
    print("4. Tally milkshakes, and show percent of each flavour")

    choice = input("Please enter your choice (1-4): ")

    if choice == "1":
        chocolate = input ("How many chocolate milkshakes were ordered? ")
        if chocolate.isnumeric():
            chocolate = int(chocolate)
        else:
            chocolate = 0
            print("Invalid input, please enter a number.")


    if choice == "2":
        vanilla = input("How many vanilla milkshakes were ordered? ")
        if vanilla.isnumeric():
            vanilla = int(vanilla)
        else:
            vanilla = 0
            print("Invalid input, please enter a number.")

    if choice == "3":
        strawberry = input("How many strawberry milkshakes were ordered? ")
        if strawberry.isnumeric():
            strawberry = int(strawberry)
        else:
            strawberry = 0
            print("Invalid input, please enter a number.")

if choice == "4":
        total = chocolate + vanilla + strawberry
        if total == 0 and (chocolate == 0 and vanilla == 0 and strawberry == 0): 
            print("No numbers entered yet.")
        if total > 0:
            chocolate_percent = (chocolate / total) * 100
            vanilla_percent = (vanilla / total) * 100
            strawberry_percent = (strawberry / total) * 100
            print(f"Total milkshakes ordered: {total}")
            print(f"Chocolate: {chocolate} ({chocolate_percent,1}%)")
            print(f"Vanilla: {vanilla} ({vanilla_percent,1}%)")
            print(f"Strawberry: {strawberry} ({strawberry_percent,1}%)")
        print("Exiting the program. have a nice day!")



# End of program



