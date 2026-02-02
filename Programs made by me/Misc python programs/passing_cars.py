# Author: Kyle Chapman
# Gui Made by: Jack Lidster
# Date: November 27, 2025
# Description:
# This program uses a tkinter UI to help someone determine whether
# they should pass another car.

from tkinter import *
from idlelib.tooltip import Hovertip

WINDOW_WIDTH = 425
WINDOW_HEIGHT = 225
WINDOW_MIN_WIDTH = 425
WINDOW_MIN_HEIGHT = 225

window = Tk()

window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.minsize(width = WINDOW_MIN_WIDTH, height = WINDOW_MIN_HEIGHT)

window.title("Should I Pass?")

def calculate():
    try:
        MINUTES_PER_HOUR = 60

        # Get the value from entry_speed_1 and treat it as a number.
        speed_one = float(entry_current_speed_1.get())
        # Get the value from entry_speed_2 and treat it as a number.
        speed_two = float(entry_current_speed_2.get())

        low_speed = min((speed_one, speed_two))
        high_speed = max((speed_one, speed_two))

        speed_difference = high_speed - low_speed

        speed_difference_seconds = speed_difference / MINUTES_PER_HOUR

        label_output.configure(text = "Going from " + str(round(low_speed, 1)) + "km/h to " + str(round(high_speed, 1)) + \
                              "km/h can gain you " + str(round(speed_difference_seconds, 2)) + " kilometres per minute.")
        
    # If they don’t both have numbers:
    except:
        # Show an error message in the output labels
        label_output.configure(text = "Error: speed entries must be numeric.")

def reset():
    entry_current_speed_1.delete(0, END)
    entry_current_speed_2.delete(0, END)
    label_output.configure(text = "")
    entry_current_speed_1.focus()

def on_enter_key(event):
    calculate()
def on_escape_key(event):
    reset()
# Now you need to set up the widgets!
# Note that if you use the exact names I did in the functions above, you won't need to modify those.
# If you use a different naming scheme, expect the functions to require some changes.


# Row 0 widgets.
# Add widgets for all rows, based on your plan.
Label_current_speed_1 = Label(window, text = "Input your current speed (km/h):")
Label_current_speed_1.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = E)
entry_current_speed_1 = Entry(window, width = 30)
entry_current_speed_1.grid(row = 0, column = 1, padx = 10, pady = 10, sticky = W)
Hovertip(entry_current_speed_1, "Enter the speed of the first car in kilometres per hour.")
# Row 1 widgets.
Label_current_speed_2 = Label(window, text = "Input your desired speed (km/h):")
Label_current_speed_2.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = E)
entry_current_speed_2 = Entry(window, width = 30)
entry_current_speed_2.grid(row = 1, column = 1, padx = 10, pady = 10, sticky = W)
Hovertip(entry_current_speed_2, "Enter the speed of the second car in kilometres per hour.")
# Row 2 widgets.
button_calculate = Button(window, text = "Calculate", command = calculate)
button_calculate.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = E)
button_reset = Button(window, text = "Reset", command = reset)
button_reset.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = W)
button_exit = Button(window, text = "Exit", command = window.destroy)
button_exit.grid(row = 2, column = 1, padx = 10, pady = 10, sticky = E)
# Row 3 widgets.
label_output = Label(window, width=50, height=4, wraplength=300, justify=LEFT, relief=SUNKEN, borderwidth=2)
label_output.grid(row = 3, column = 0, columnspan = 2, padx = 10, pady = 10)
Hovertip(label_output, "This area displays the result of the calculation or error messages.")
# Add hotkey support.
window.bind('<Return>', on_enter_key)
window.bind('<Escape>', on_escape_key)
# Anything else?
for row in range(4):
    window.grid_rowconfigure(row, weight=1)
for collumn in range(2):
    window.grid_columnconfigure(collumn, weight=1)

window.mainloop()

