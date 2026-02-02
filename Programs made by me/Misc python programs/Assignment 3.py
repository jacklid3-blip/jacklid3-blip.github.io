# Author: Jack Lidster
# Date: 2025-12-02
# Description: 
# This program uses a tkinter UI to help someone calculate
# their bmi and if they are underweight, healthy, overweight, or obese.
from tkinter import *
from idlelib.tooltip import Hovertip

WINDOW_WIDTH = 425
WINDOW_HEIGHT = 225
WINDOW_MIN_WIDTH = 425
WINDOW_MIN_HEIGHT = 225

# Color palette
COLOR_BG = "#e6f7ff"       # light blue background
ACCENT = "#003366"         # dark blue for text
ENTRY_BG = "#fffde6"       # light yellow for entries
ENTRY_BORDER = "#99ccff"   # entry border highlight
BUTTON_CALC_BG = "#28a745" # green
BUTTON_RESET_BG = "#dc3545"# red
BUTTON_FG = "#ffffff"      # white text on buttons
OUTPUT_BG = "#f0fbff"      # very light blue for output area

# Category background colors for output
OUT_BG_SEVERE = "#cce5ff"  # light blue
OUT_BG_UNDER = "#fff3cd"   # light yellow/orange
OUT_BG_HEALTHY = "#d4edda" # light green
OUT_BG_OVER = "#ffe5b4"    # peach/light orange
OUT_BG_OBESE = "#f8d7da"   # light red/pink

window = Tk()

window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

window.title("BMI Calculator")
window.configure(bg=COLOR_BG)

def calculate():
    try:
        BMI_FACTOR = 703  # conversion factor for imperial units (lb/in^2)

        # Get the value from entry_height and treat it as a number.
        height_in = float(entry_height.get())
        # Validate height range
        if height_in < 24 or height_in > 120:
            label_output.configure(text="Error: height must be between 24 and 120 inches.",
                                   fg="#b30000", bg="#ffe6e6")
            entry_height.focus()
            return

        # Get the value from entry_weight and treat it as a number.
        weight_lb = float(entry_weight.get())
        # Validate weight minimum
        if weight_lb < 30:
            label_output.configure(text="Error: weight must be at least 30 pounds.",
                                   fg="#b30000", bg="#ffe6e6")
            entry_weight.focus()
            return

        bmi = (weight_lb / (height_in ** 2)) * BMI_FACTOR
        if bmi < 16:
            category = "severely underweight"
            out_bg = OUT_BG_SEVERE
        elif bmi < 18.5:
            category = "underweight"
            out_bg = OUT_BG_UNDER
        elif bmi < 25:
            category = "healthy"
            out_bg = OUT_BG_HEALTHY
        elif bmi < 30:
            category = "overweight"
            out_bg = OUT_BG_OVER
        else:
            category = "obese"
            out_bg = OUT_BG_OBESE

        label_output.configure(text = f"Your BMI is {bmi:.1f}, which is considered {category}.",
                               fg=ACCENT, bg=out_bg)
        
    except ValueError:
        # If they don’t both have numbers:
        label_output.configure(text = "Error: height and weight entries must be numeric.",
                               fg="#b30000", bg="#ffe6e6")
        entry_height.focus()
    except Exception as e:
        label_output.configure(text = f"Error: {e}",
                               fg="#b30000", bg="#ffe6e6")
        entry_height.focus()

def reset():
    entry_height.delete(0, END)
    entry_weight.delete(0, END)
    label_output.configure(text = "", bg=OUTPUT_BG)
    entry_height.focus()

def on_enter_key(event):
    calculate()
def on_escape_key(event):
    reset()

# Banner/title (row 0)
label_banner = Label(window, text="BMI Calculator", bg=ACCENT, fg=BUTTON_FG,
                     font=("Segoe UI", 14, "bold"), padx=8, pady=6)
label_banner.grid(row=0, column=0, columnspan=2, sticky=E+W, padx=10, pady=(10, 5))

# Row 1 widgets.
label_height = Label(window, text="Input your height (inches):",
                     bg=COLOR_BG, fg=ACCENT, font=("Segoe UI", 10))
label_height.grid(row=1, column=0, padx=10, pady=6, sticky=E)
entry_height = Entry(window, width=30, bg=ENTRY_BG, fg="#003333", insertbackground="#003333",
                     relief="groove", borderwidth=2, highlightthickness=2,
                     highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT)
entry_height.grid(row=1, column=1, padx=10, pady=6)
Hovertip(entry_height, "Enter height in inches (ex, 24 - 120 in).")

# Row 2 widgets.
label_weight = Label(window, text = "Input your weight (pounds):",
                     bg=COLOR_BG, fg=ACCENT, font=("Segoe UI", 10))
label_weight.grid(row = 2, column = 0, padx = 10, pady = 6, sticky = E)
entry_weight = Entry(window, width = 30, bg=ENTRY_BG, fg="#003333", insertbackground="#003333",
                     relief="groove", borderwidth=2, highlightthickness=2,
                     highlightbackground=ENTRY_BORDER, highlightcolor=ACCENT)
entry_weight.grid(row = 2, column = 1, padx = 10, pady = 6)
Hovertip(entry_weight, "Enter weight in pounds (ex, 30 - 999 lb).")

# Row 3 widgets.
button_calculate = Button(window, text = "Calculate BMI", command = calculate,
                          bg=BUTTON_CALC_BG, fg=BUTTON_FG, activebackground="#1e7a34",
                          relief="raised", padx=10, pady=5)
button_calculate.grid(row = 3, column = 0, padx = 10, pady = 8, sticky=E+W)
button_reset = Button(window, text = "Reset", command = reset,
                      bg=BUTTON_RESET_BG, fg=BUTTON_FG, activebackground="#a71d2a",
                      relief="raised", padx=10, pady=5)
button_reset.grid(row = 3, column = 1, padx = 10, pady = 8, sticky=E+W)
button_exit = Button(window, text = "Exit", command = window.destroy,
                     bg="#6c757d", fg=BUTTON_FG, activebackground="#5a6268",
                     relief="raised", padx=10, pady=5)
# (optional) place exit below everything
button_exit.grid(row=5, column=0, columnspan=2, padx=10, pady=(0,10), sticky=E)

# Row 4 widgets.
label_output = Label(window, text = "", wraplength=400, justify=LEFT,
                     bg=OUTPUT_BG, fg=ACCENT, relief="sunken", borderwidth=2, anchor=W,
                     padx=6, pady=6)
label_output.grid(row = 4, column = 0, columnspan=2, padx = 10, pady = 6, sticky=E+W)

# Hotkeys
window.bind('<Return>', on_enter_key)
window.bind('<Escape>', on_escape_key)
# Extra stuff
for row in range(6):
    window.grid_rowconfigure(row, weight=1)
for col in range(2):
    window.grid_columnconfigure(col, weight=1)

window.mainloop()